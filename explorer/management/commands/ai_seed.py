"""
Management command: ai_seed
Uses the Claude API to generate and import historical content into the database.

Usage:
  uv run python manage.py ai_seed "Create detailed events during Peter the Great's reign"
  uv run python manage.py ai_seed "Add relationships between Alexander II and the serfs" --era romanov-dynasty
  uv run python manage.py ai_seed "..." --dry-run
"""
import json
import os
import sys
import textwrap

from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

from explorer.models import Era, Period, Person, Event, Relationship

SYSTEM_PROMPT = textwrap.dedent("""
You are a historian and Django data architect. Your job is to generate structured
historical content for a Django application called History Explorer.

## Data Models

Return a JSON object with these optional top-level arrays:

```json
{
  "eras": [...],
  "periods": [...],
  "people": [...],
  "events": [...],
  "relationships": [...]
}
```

### Era fields
- name (str, required)
- slug (str, required — kebab-case, unique)
- tagline (str ≤300 chars, required)
- summary (str, 2–4 sentences, required)
- body (str, rich Markdown, optional)
- start_year (int, required)
- end_year (int or null)
- color_accent (str, CSS hex like "#8b1a1a", optional)
- order (int, optional)

### Period fields
- era_slug (str, required — must match an existing era slug)
- name (str, required)
- slug (str, required — kebab-case, unique)
- summary (str, 2–4 sentences, required)
- body (str, rich Markdown, optional)
- start_year (int, required)
- end_year (int or null)
- order (int, optional)

### Person fields
- era_slug (str, required)
- period_slug (str or null — matches existing period)
- name (str, required)
- slug (str, required — kebab-case, unique)
- title (str, e.g. "Tsar of All Russia", optional)
- summary (str, 2–4 sentences, required)
- body (str, rich Markdown with ## headers, optional — aim for 400–800 words)
- birth_year (int or null)
- death_year (int or null)
- reign_start (int or null)
- reign_end (int or null)
- nationality (str, optional)
- latitude (float or null — decimal degrees of the person's primary seat of power or birthplace, e.g. 59.9311)
- longitude (float or null — decimal degrees, e.g. 30.3609)
- region (str — broad geographic region for timeline swim-lanes, e.g. "Russia", "France", "Britain", "Iberia", "Low Countries", "Central Europe")

### Event fields
- era_slug (str, required)
- period_slug (str or null)
- name (str, required)
- slug (str, required — kebab-case, unique)
- event_type (str — one of: battle, treaty, revolution, reform, disaster, cultural, political, other)
- summary (str, 2–4 sentences, required)
- body (str, rich Markdown, optional)
- year (int, required)
- end_year (int or null)
- location (str, optional — human-readable place, e.g. "Austerlitz, Moravia")
- latitude (float or null — decimal degrees where the event occurred, e.g. 49.1530)
- longitude (float or null — decimal degrees, e.g. 16.8760)
- region (str — broad geographic region for timeline swim-lanes, e.g. "Russia", "France", "Britain", "Iberia", "Low Countries", "Central Europe")

### Relationship fields
Connects any two entities (person, event, period, era) by slug.
- from_slug (str, required — slug of the source entity)
- from_type (str, required — one of: person, event, period, era)
- to_slug (str, required — slug of the target entity)
- to_type (str, required — one of: person, event, period, era)
- relationship_type (str, required — one of: parent, child, spouse, rival, ally, advisor,
  subject, influenced, participated, caused, was_affected_by, ordered, led, survived,
  followed, prevented, ruled, lived_during, defined, ended, marked_start_of)
- description (str, 1–2 sentences explaining the connection, optional)
- strength (int 1–5, default 3)
- is_bidirectional (bool, default false)

## Rules
- All slugs must be kebab-case and unique within their type.
- Body fields support Markdown: ## headers, **bold**, *italic*, lists, blockquotes.
- Cross-link entities using [[slug]] syntax in body text (e.g., [[peter-i]], [[battle-of-poltava]]).
- summary fields are plain teasers shown on cards — do NOT put [[slug]] cross-references in summary, only in body.
- ALWAYS provide latitude, longitude, and region for every person and event so they
  appear on the globe and the cross-region timeline. Reuse the exact region names listed
  above when they apply, so timeline lanes stay consistent.
- Only return entities you are creating/updating — omit types you are not adding.
- Return ONLY valid JSON. No markdown fences, no explanation outside the JSON.
""").strip()


def _resolve_entity(from_type, from_slug):
    model_map = {'person': Person, 'event': Event, 'period': Period, 'era': Era}
    model = model_map.get(from_type)
    if model is None:
        return None, None
    try:
        obj = model.objects.get(slug=from_slug)
        ct = ContentType.objects.get_for_model(model)
        return ct, obj.pk
    except model.DoesNotExist:
        return None, None


def _import_data(data, stdout, dry_run=False):
    stats = {'eras': 0, 'periods': 0, 'people': 0, 'events': 0, 'relationships': 0}

    for item in data.get('eras', []):
        slug = item.get('slug')
        if not slug:
            stdout.write(f'  SKIP era: missing slug')
            continue
        defaults = {k: v for k, v in item.items() if k != 'slug'}
        if not dry_run:
            obj, created = Era.objects.update_or_create(slug=slug, defaults=defaults)
        stdout.write(f"  Era: {item.get('name')} ({slug})")
        stats['eras'] += 1

    for item in data.get('periods', []):
        slug = item.get('slug')
        era_slug = item.pop('era_slug', None)
        if not slug or not era_slug:
            stdout.write(f'  SKIP period: missing slug or era_slug')
            continue
        try:
            era = Era.objects.get(slug=era_slug)
        except Era.DoesNotExist:
            stdout.write(f'  SKIP period {slug}: era "{era_slug}" not found')
            continue
        defaults = {k: v for k, v in item.items() if k != 'slug'}
        defaults['era'] = era
        if not dry_run:
            Period.objects.update_or_create(slug=slug, defaults=defaults)
        stdout.write(f"  Period: {item.get('name')} ({slug})")
        stats['periods'] += 1

    for item in data.get('people', []):
        slug = item.get('slug')
        era_slug = item.pop('era_slug', None)
        period_slug = item.pop('period_slug', None)
        if not slug or not era_slug:
            stdout.write(f'  SKIP person: missing slug or era_slug')
            continue
        try:
            era = Era.objects.get(slug=era_slug)
        except Era.DoesNotExist:
            stdout.write(f'  SKIP person {slug}: era "{era_slug}" not found')
            continue
        period = None
        if period_slug:
            period = Period.objects.filter(slug=period_slug).first()
        defaults = {k: v for k, v in item.items() if k != 'slug'}
        defaults['era'] = era
        defaults['period'] = period
        defaults.setdefault('status', 'published')
        if not dry_run:
            Person.objects.update_or_create(slug=slug, defaults=defaults)
        stdout.write(f"  Person: {item.get('name')} ({slug})")
        stats['people'] += 1

    for item in data.get('events', []):
        slug = item.get('slug')
        era_slug = item.pop('era_slug', None)
        period_slug = item.pop('period_slug', None)
        if not slug or not era_slug:
            stdout.write(f'  SKIP event: missing slug or era_slug')
            continue
        try:
            era = Era.objects.get(slug=era_slug)
        except Era.DoesNotExist:
            stdout.write(f'  SKIP event {slug}: era "{era_slug}" not found')
            continue
        period = None
        if period_slug:
            period = Period.objects.filter(slug=period_slug).first()
        defaults = {k: v for k, v in item.items() if k != 'slug'}
        defaults['era'] = era
        defaults['period'] = period
        defaults.setdefault('status', 'published')
        if not dry_run:
            Event.objects.update_or_create(slug=slug, defaults=defaults)
        stdout.write(f"  Event: {item.get('name')} ({slug})")
        stats['events'] += 1

    for item in data.get('relationships', []):
        from_slug = item.get('from_slug')
        from_type = item.get('from_type')
        to_slug = item.get('to_slug')
        to_type = item.get('to_type')
        rel_type = item.get('relationship_type')
        if not all([from_slug, from_type, to_slug, to_type, rel_type]):
            stdout.write(f'  SKIP relationship: missing required fields')
            continue
        from_ct, from_id = _resolve_entity(from_type, from_slug)
        to_ct, to_id = _resolve_entity(to_type, to_slug)
        if not from_ct or not to_ct:
            stdout.write(
                f'  SKIP relationship {from_slug}→{to_slug}: entity not found'
            )
            continue
        if not dry_run:
            Relationship.objects.update_or_create(
                from_entity_type=from_ct,
                from_entity_id=from_id,
                to_entity_type=to_ct,
                to_entity_id=to_id,
                relationship_type=rel_type,
                defaults={
                    'description': item.get('description', ''),
                    'strength': item.get('strength', 3),
                    'is_bidirectional': item.get('is_bidirectional', False),
                }
            )
        stdout.write(f"  Relationship: {from_slug} →[{rel_type}]→ {to_slug}")
        stats['relationships'] += 1

    return stats


class Command(BaseCommand):
    help = 'Generate and import historical content using the Claude API'

    def add_arguments(self, parser):
        parser.add_argument(
            'prompt',
            nargs='?',
            help='Natural language description of content to generate',
        )
        parser.add_argument('--era', help='Slug of an era for context (e.g. romanov-dynasty)')
        parser.add_argument('--dry-run', action='store_true', help='Parse but do not save')
        parser.add_argument(
            '--model',
            default='claude-sonnet-4-6',
            help='Claude model to use (default: claude-sonnet-4-6)',
        )
        parser.add_argument(
            '--file',
            help='Load JSON directly from a file instead of calling the API',
        )

    def handle(self, *args, **options):
        try:
            import anthropic
        except ImportError:
            raise CommandError(
                'anthropic package not installed. Run: uv add anthropic'
            )

        if options.get('file'):
            with open(options['file']) as f:
                data = json.load(f)
            self._apply(data, options)
            return

        prompt = options.get('prompt')
        if not prompt:
            raise CommandError('Provide a prompt or use --file to load JSON directly.')

        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise CommandError(
                'ANTHROPIC_API_KEY environment variable not set. '
                'Add it to .env or export it in your shell.'
            )

        # Build context from existing DB
        context_parts = ['## Existing content in the database\n']
        if options.get('era'):
            try:
                era = Era.objects.get(slug=options['era'])
                context_parts.append(f'### Era: {era.name} ({era.slug})')
                context_parts.append(f'Years: {era.start_year}–{era.end_year}')
                periods = era.periods.filter(status='published').order_by('order')
                if periods:
                    context_parts.append('\nPeriods:')
                    for p in periods:
                        context_parts.append(f'  - {p.name} ({p.slug}, {p.start_year}–{p.end_year})')
                people = era.people.filter(status='published').order_by('reign_start')
                if people:
                    context_parts.append('\nPeople (tsars/rulers):')
                    for p in people:
                        context_parts.append(
                            f'  - {p.name} ({p.slug}, '
                            f'reign {p.reign_start}–{p.reign_end})'
                        )
                events = era.events.filter(status='published').order_by('year')[:20]
                if events:
                    context_parts.append('\nEvents:')
                    for e in events:
                        context_parts.append(f'  - {e.year}: {e.name} ({e.slug})')
            except Era.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'Era "{options["era"]}" not found — continuing without era context'
                ))
        else:
            eras = Era.objects.filter(status='published')
            if eras:
                context_parts.append('Eras: ' + ', '.join(f'{e.name} ({e.slug})' for e in eras))

        context = '\n'.join(context_parts)
        full_prompt = f'{context}\n\n## Request\n\n{prompt}'

        self.stdout.write(f'Calling {options["model"]}...')
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=options['model'],
            max_tokens=8096,
            system=SYSTEM_PROMPT,
            messages=[{'role': 'user', 'content': full_prompt}],
        )

        raw = message.content[0].text.strip()

        # Strip markdown fences if present
        if raw.startswith('```'):
            lines = raw.split('\n')
            raw = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CommandError(
                f'Claude returned invalid JSON: {exc}\n\nRaw response:\n{raw[:500]}'
            )

        self._apply(data, options)

    def _apply(self, data, options):
        dry_run = options.get('dry_run', False)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no changes will be saved'))

        stats = _import_data(data, self.stdout, dry_run=dry_run)
        total = sum(stats.values())
        label = 'Would create/update' if dry_run else 'Created/updated'
        self.stdout.write(self.style.SUCCESS(
            f'\n{label}: {stats["eras"]} eras, {stats["periods"]} periods, '
            f'{stats["people"]} people, {stats["events"]} events, '
            f'{stats["relationships"]} relationships ({total} total)'
        ))
