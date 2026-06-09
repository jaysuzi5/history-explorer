import json
from django.shortcuts import get_object_or_404, render
from django.http import Http404
from django.db.models import Q, Count
from django.contrib.contenttypes.models import ContentType

from .models import Era, Period, Person, Event, Relationship


def galaxy(request):
    eras = Era.objects.filter(status='published').order_by('order')
    return render(request, 'explorer/galaxy.html', {'eras': eras})


def globe(request):
    eras = Era.objects.filter(status='published').order_by('order')
    return render(request, 'explorer/globe.html', {
        'eras': eras,
        'globe_json': json.dumps(build_globe_data()),
        'breadcrumbs': [
            {'label': 'Home', 'url': '/'},
            {'label': 'Globe', 'url': None},
        ],
    })


def timeline(request):
    eras = Era.objects.filter(status='published').order_by('order')
    return render(request, 'explorer/timeline.html', {
        'eras': eras,
        'timeline_json': json.dumps(build_region_timeline_data()),
        'breadcrumbs': [
            {'label': 'Home', 'url': '/'},
            {'label': 'Timeline', 'url': None},
        ],
    })


def era_overview(request, era_slug):
    era = get_object_or_404(Era, slug=era_slug, status='published')
    people = list(era.people.filter(status='published'))
    events = list(era.events.filter(status='published'))
    periods = list(era.periods.filter(status='published'))

    return render(request, 'explorer/era_overview.html', {
        'era': era,
        'people': people,
        'events': events,
        'periods': periods,
        'graph_json': json.dumps(build_graph_data_for_era(era, people, events, periods)),
        'timeline_json': json.dumps(build_timeline_data(people, events, periods)),
        'breadcrumbs': [
            {'label': 'Home', 'url': '/'},
            {'label': era.name, 'url': None},
        ],
    })


def period_detail(request, era_slug, period_slug):
    era = get_object_or_404(Era, slug=era_slug, status='published')
    period = get_object_or_404(Period, slug=period_slug, era=era, status='published')
    people = list(period.people.filter(status='published'))
    events = list(period.events.filter(status='published'))

    return render(request, 'explorer/period_detail.html', {
        'era': era,
        'period': period,
        'people': people,
        'events': events,
        'breadcrumbs': [
            {'label': 'Home', 'url': '/'},
            {'label': era.name, 'url': era.get_absolute_url()},
            {'label': period.name, 'url': None},
        ],
    })


def person_detail(request, era_slug, person_slug):
    era = get_object_or_404(Era, slug=era_slug, status='published')
    person = get_object_or_404(Person, slug=person_slug, era=era, status='published')

    return render(request, 'explorer/person_detail.html', {
        'era': era,
        'person': person,
        'relationships': _resolved_relationships(person),
        'graph_json': json.dumps(build_graph_data_for_entity(person)),
        'breadcrumbs': [
            {'label': 'Home', 'url': '/'},
            {'label': era.name, 'url': era.get_absolute_url()},
            {'label': person.name, 'url': None},
        ],
    })


def event_detail(request, era_slug, event_slug):
    era = get_object_or_404(Era, slug=era_slug, status='published')
    event = get_object_or_404(Event, slug=event_slug, era=era, status='published')

    return render(request, 'explorer/event_detail.html', {
        'era': era,
        'event': event,
        'relationships': _resolved_relationships(event),
        'graph_json': json.dumps(build_graph_data_for_entity(event)),
        'breadcrumbs': [
            {'label': 'Home', 'url': '/'},
            {'label': era.name, 'url': era.get_absolute_url()},
            {'label': event.name, 'url': None},
        ],
    })


def connection_detail(request, era_slug, from_slug, to_slug):
    era = get_object_or_404(Era, slug=era_slug, status='published')
    from_entity = _resolve_entity(from_slug)
    to_entity = _resolve_entity(to_slug)

    if not from_entity or not to_entity:
        raise Http404

    from_ct = ContentType.objects.get_for_model(from_entity)
    to_ct = ContentType.objects.get_for_model(to_entity)

    relationship = get_object_or_404(
        Relationship,
        from_entity_type=from_ct, from_entity_id=from_entity.pk,
        to_entity_type=to_ct, to_entity_id=to_entity.pk,
    )

    return render(request, 'explorer/connection_detail.html', {
        'era': era,
        'from_entity': from_entity,
        'from_entity_type': from_ct.model,
        'to_entity': to_entity,
        'to_entity_type': to_ct.model,
        'relationship': relationship,
        'breadcrumbs': [
            {'label': 'Home', 'url': '/'},
            {'label': era.name, 'url': era.get_absolute_url()},
            {'label': from_entity.name, 'url': from_entity.get_absolute_url()},
            {'label': f'↔ {to_entity.name}', 'url': None},
        ],
    })


# ── internal helpers ──────────────────────────────────────────────────────────

def _resolve_entity(slug):
    for Model in (Person, Event, Period, Era):
        try:
            return Model.objects.get(slug=slug, status='published')
        except Model.DoesNotExist:
            continue
    return None


def _resolved_relationships(entity):
    """Return list of dicts: {rel, other_entity, is_outgoing}."""
    ct = ContentType.objects.get_for_model(entity)
    rels = Relationship.objects.filter(
        Q(from_entity_type=ct, from_entity_id=entity.pk) |
        Q(to_entity_type=ct, to_entity_id=entity.pk)
    ).select_related('from_entity_type', 'to_entity_type')

    result = []
    for rel in rels:
        is_outgoing = rel.from_entity_type == ct and rel.from_entity_id == entity.pk
        other = rel.to_entity if is_outgoing else rel.from_entity
        if other is not None:
            result.append({'rel': rel, 'other': other, 'is_outgoing': is_outgoing})
    return result


def _rel_counts(ct, pks):
    """Return {pk: total_relationship_count} for importance scoring."""
    counts = {pk: 0 for pk in pks}
    for row in (Relationship.objects
                .filter(from_entity_type=ct, from_entity_id__in=pks)
                .values('from_entity_id').annotate(c=Count('id'))):
        counts[row['from_entity_id']] = counts[row['from_entity_id']] + row['c']
    for row in (Relationship.objects
                .filter(to_entity_type=ct, to_entity_id__in=pks)
                .values('to_entity_id').annotate(c=Count('id'))):
        counts[row['to_entity_id']] = counts[row['to_entity_id']] + row['c']
    return counts


# ── globe builder ─────────────────────────────────────────────────────────────

def build_globe_data():
    """Points for every geocoded Person/Event, jittered so co-located points spread."""
    import math

    points = []
    for p in Person.objects.filter(status='published',
                                   latitude__isnull=False).select_related('era'):
        when = p.reign_start or p.birth_year
        points.append({
            'lat': p.latitude, 'lng': p.longitude, 'type': 'person',
            'name': p.name, 'url': p.get_absolute_url(),
            'era': p.era.name, 'eraSlug': p.era.slug, 'eraColor': p.era.color_accent,
            'region': p.region, 'year': when, 'summary': p.summary[:160],
        })
    for e in Event.objects.filter(status='published',
                                  latitude__isnull=False).select_related('era'):
        points.append({
            'lat': e.latitude, 'lng': e.longitude, 'type': 'event',
            'name': e.name, 'url': e.get_absolute_url(),
            'era': e.era.name, 'eraSlug': e.era.slug, 'eraColor': e.era.color_accent,
            'region': e.region, 'year': e.year, 'summary': e.summary[:160],
        })

    # Spread points sharing the same coordinate around a small circle so the
    # globe doesn't stack them into a single unclickable dot.
    buckets = {}
    for pt in points:
        key = (round(pt['lat'], 3), round(pt['lng'], 3))
        buckets.setdefault(key, []).append(pt)
    for group in buckets.values():
        if len(group) == 1:
            continue
        radius = 0.55
        for i, pt in enumerate(group):
            angle = 2 * math.pi * i / len(group)
            pt['lat'] = round(pt['lat'] + radius * math.sin(angle), 5)
            pt['lng'] = round(pt['lng'] + radius * math.cos(angle), 5)

    return {'points': points}


# ── cross-region timeline builder ──────────────────────────────────────────────

# West-to-east ordering of swim-lanes; anything else falls to the bottom A–Z.
REGION_ORDER = ['Britain', 'Iberia', 'France', 'Low Countries',
                'Central Europe', 'Russia']


def _region_rank(region):
    try:
        return (0, REGION_ORDER.index(region))
    except ValueError:
        return (1, region)


def build_region_timeline_data():
    """Items grouped by region across all eras, colored by era.

    People with a reign show a reign range; other people show a lifespan range
    (lighter); events show a point or a year-span range. Each item carries its
    start/end *years* so the front-end can compute what is active at any scrubbed year.
    """
    items = []
    regions = set()

    def style_for(color, faint=False):
        bg = f'{color}22' if faint else f'{color}55'
        return f'background-color: {bg}; border-color: {color}; color: #f0e6c8;'

    for p in Person.objects.filter(status='published').select_related('era'):
        region = p.region or 'Other'
        color = p.era.color_accent
        if p.reign_start:
            start_y, end_y, faint, kind = p.reign_start, p.reign_end, False, 'reign'
        elif p.birth_year:
            start_y, end_y, faint, kind = p.birth_year, p.death_year, True, 'life'
        else:
            continue
        regions.add(region)
        item = {
            'id': f'p-{p.slug}', 'group': region, 'content': p.name,
            'start': f'{start_y}-06-01', 'type': 'range' if end_y else 'point',
            'url': p.get_absolute_url(), 'title': p.summary[:120],
            'style': style_for(color, faint), 'className': f'tl-{kind}',
            'era': p.era.name, 'eraColor': color, 'kind': kind,
            'startYear': start_y, 'endYear': end_y or start_y,
        }
        if end_y:
            item['end'] = f'{end_y}-06-01'
        items.append(item)

    for e in Event.objects.filter(status='published').select_related('era'):
        region = e.region or 'Other'
        color = e.era.color_accent
        regions.add(region)
        item = {
            'id': f'e-{e.slug}', 'group': region, 'content': e.name,
            'start': f'{e.year}-06-01', 'type': 'range' if e.end_year else 'point',
            'url': e.get_absolute_url(), 'title': e.summary[:120],
            'style': style_for(color), 'className': 'tl-event',
            'era': e.era.name, 'eraColor': color, 'kind': 'event',
            'startYear': e.year, 'endYear': e.end_year or e.year,
        }
        if e.end_year:
            item['end'] = f'{e.end_year}-06-01'
        items.append(item)

    groups = [{'id': r, 'content': r}
              for r in sorted(regions, key=_region_rank)]
    return {'items': items, 'groups': groups}


# ── graph builders ────────────────────────────────────────────────────────────

def build_graph_data_for_era(era, people, events, periods):
    person_ct = ContentType.objects.get_for_model(Person)
    event_ct = ContentType.objects.get_for_model(Event)
    period_ct = ContentType.objects.get_for_model(Period)

    person_pks = [p.pk for p in people]
    event_pks = [e.pk for e in events]
    period_pks = [p.pk for p in periods]

    p_counts = _rel_counts(person_ct, person_pks)
    e_counts = _rel_counts(event_ct, event_pks)
    pr_counts = _rel_counts(period_ct, period_pks)

    nodes = []
    node_id_set = set()

    for p in people:
        nid = f'person-{p.slug}'
        node_id_set.add(nid)
        nodes.append({'data': {
            'id': nid, 'label': p.name, 'type': 'person',
            'url': p.get_absolute_url(), 'summary': p.summary[:150],
            'importance': min(10, max(1, p_counts.get(p.pk, 0) + 1)),
        }})

    for e in events:
        nid = f'event-{e.slug}'
        node_id_set.add(nid)
        nodes.append({'data': {
            'id': nid, 'label': e.name, 'type': 'event',
            'url': e.get_absolute_url(), 'summary': e.summary[:150],
            'importance': min(10, max(1, e_counts.get(e.pk, 0) + 1)),
        }})

    for p in periods:
        nid = f'period-{p.slug}'
        node_id_set.add(nid)
        nodes.append({'data': {
            'id': nid, 'label': p.name, 'type': 'period',
            'url': p.get_absolute_url(), 'summary': p.summary[:150],
            'importance': min(10, max(1, pr_counts.get(p.pk, 0) + 1)),
        }})

    ct_to_map = {
        person_ct.pk: {p.pk: f'person-{p.slug}' for p in people},
        event_ct.pk: {e.pk: f'event-{e.slug}' for e in events},
        period_ct.pk: {p.pk: f'period-{p.slug}' for p in periods},
    }
    all_pks_by_ct = {
        person_ct.pk: person_pks,
        event_ct.pk: event_pks,
        period_ct.pk: period_pks,
    }

    edges = []
    seen_rels = set()

    for ct_pk, pks in all_pks_by_ct.items():
        if not pks:
            continue
        for rel in Relationship.objects.filter(
            from_entity_type_id=ct_pk, from_entity_id__in=pks,
        ).select_related('from_entity_type', 'to_entity_type'):
            if rel.pk in seen_rels:
                continue
            src = ct_to_map.get(rel.from_entity_type_id, {}).get(rel.from_entity_id)
            dst = ct_to_map.get(rel.to_entity_type_id, {}).get(rel.to_entity_id)
            if src and dst:
                seen_rels.add(rel.pk)
                edges.append({'data': {
                    'id': f'rel-{rel.pk}', 'source': src, 'target': dst,
                    'label': rel.get_relationship_type_display(),
                    'strength': rel.strength, 'url': None,
                }})

    return {'nodes': nodes, 'edges': edges}


def build_graph_data_for_entity(entity):
    ct = ContentType.objects.get_for_model(entity)
    entity_type = ct.model
    central_id = f'{entity_type}-{entity.slug}'

    nodes = [{'data': {
        'id': central_id, 'label': entity.name,
        'type': entity_type, 'url': entity.get_absolute_url(),
        'summary': entity.summary[:150], 'importance': 10, 'isCentral': True,
    }}]
    edges = []
    seen_nodes = {central_id}

    rels = Relationship.objects.filter(
        Q(from_entity_type=ct, from_entity_id=entity.pk) |
        Q(to_entity_type=ct, to_entity_id=entity.pk)
    ).select_related('from_entity_type', 'to_entity_type')

    for rel in rels:
        is_from = rel.from_entity_type == ct and rel.from_entity_id == entity.pk
        other = rel.to_entity if is_from else rel.from_entity
        if other is None:
            continue

        other_ct = rel.to_entity_type if is_from else rel.from_entity_type
        other_id = f'{other_ct.model}-{other.slug}'

        if other_id not in seen_nodes:
            seen_nodes.add(other_id)
            nodes.append({'data': {
                'id': other_id, 'label': other.name,
                'type': other_ct.model, 'url': other.get_absolute_url(),
                'summary': other.summary[:150], 'importance': max(3, rel.strength * 2),
            }})

        src = central_id if is_from else other_id
        dst = other_id if is_from else central_id
        edges.append({'data': {
            'id': f'rel-{rel.pk}', 'source': src, 'target': dst,
            'label': rel.get_relationship_type_display(),
            'strength': rel.strength, 'url': None,
        }})

    return {'nodes': nodes, 'edges': edges}


def build_timeline_data(people, events, periods):
    items = []

    for p in people:
        if p.reign_start:
            item = {
                'id': f'person-{p.slug}',
                'content': p.name,
                'start': f'{p.reign_start}-06-01',
                'group': 'rulers',
                'url': p.get_absolute_url(),
                'title': p.summary[:100],
            }
            if p.reign_end:
                item.update({'end': f'{p.reign_end}-06-01', 'type': 'range'})
            else:
                item['type'] = 'point'
            items.append(item)

    for e in events:
        item = {
            'id': f'event-{e.slug}',
            'content': e.name,
            'start': f'{e.year}-06-01',
            'group': 'events',
            'url': e.get_absolute_url(),
            'title': e.summary[:100],
        }
        if e.end_year:
            item.update({'end': f'{e.end_year}-06-01', 'type': 'range'})
        else:
            item['type'] = 'point'
        items.append(item)

    for p in periods:
        items.append({
            'id': f'period-bg-{p.slug}',
            'content': p.name,
            'start': f'{p.start_year}-01-01',
            'end': f'{(p.end_year or p.start_year + 10)}-12-31',
            'type': 'background',
            'group': 'periods',
        })

    groups = [
        {'id': 'rulers', 'content': 'Rulers'},
        {'id': 'events', 'content': 'Events'},
        {'id': 'periods', 'content': 'Periods'},
    ]
    return {'items': items, 'groups': groups}
