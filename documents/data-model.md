# History Explorer — Data Model

## Design Philosophy

All content entities (Era, Period, Person, Event) share a common pattern:
- `slug` for URL-safe identifiers
- `summary` (short, used in cards and graph tooltips)
- `body` (Markdown, full detail page content; may contain `[[slug]]` cross-references)
- `featured_image` for visual representation
- `status` (draft / published)
- `metadata` (JSON, flexible extra fields per entity type)

Cross-references in body text use the format `[[entity-slug]]` and are resolved to links
at render time by a template filter.

---

## Models

### Era

Top-level historical container. Maps to Level 2 in the explorer.

```
Era
├── name            CharField(200)
├── slug            SlugField(unique)
├── tagline         CharField(300)         # shown on Level 1 card
├── summary         TextField              # 1-2 paragraphs, card + hover
├── body            MarkdownxField         # full detail, supports [[slug]] links
├── featured_image  ImageField
├── start_year      IntegerField           # BCE stored as negative
├── end_year        IntegerField(null)     # null = ongoing
├── color_accent    CharField(30)          # CSS hex, used for era theming
├── icon            CharField(60)          # Bootstrap Icons class
├── order           PositiveIntegerField   # display order on landing page
├── status          CharField (draft/published)
└── created_at / updated_at
```

### Period

Sub-division within an Era. Optional — not all eras need sub-periods.

```
Period
├── era             ForeignKey(Era)
├── name            CharField(200)
├── slug            SlugField(unique)
├── summary         TextField
├── body            MarkdownxField
├── featured_image  ImageField
├── start_year      IntegerField
├── end_year        IntegerField(null)
├── order           PositiveIntegerField
└── status          CharField
```

### Person

A historical figure. Belongs to one primary Era; may be referenced across many.

```
Person
├── era             ForeignKey(Era, related_name='people')
├── period          ForeignKey(Period, null, blank)
├── name            CharField(200)
├── slug            SlugField(unique)
├── title           CharField(200, blank)  # "Tsar of Russia", "Emperor"
├── summary         TextField              # 2-3 sentence bio for cards
├── body            MarkdownxField         # full biography, [[slug]] links OK
├── featured_image  ImageField             # portrait
├── birth_year      IntegerField(null)
├── death_year      IntegerField(null)
├── reign_start     IntegerField(null)
├── reign_end       IntegerField(null)
├── nationality     CharField(100, blank)
├── tags            ManyToManyField(Tag)
├── status          CharField
└── metadata        JSONField(default=dict) # flexible extra fields
```

### Event

A historical event or turning point.

```
Event
├── era             ForeignKey(Era, related_name='events')
├── period          ForeignKey(Period, null, blank)
├── name            CharField(200)
├── slug            SlugField(unique)
├── event_type      CharField choices: battle, treaty, revolution, reform,
│                                      disaster, cultural, political, other
├── summary         TextField
├── body            MarkdownxField
├── featured_image  ImageField
├── year            IntegerField
├── end_year        IntegerField(null)     # for multi-year events
├── location        CharField(200, blank)
├── tags            ManyToManyField(Tag)
├── status          CharField
└── metadata        JSONField(default=dict)
```

### Tag

Shared across Person, Event, Era.

```
Tag
├── name            CharField(50)
└── slug            SlugField(unique)
```

### Relationship

Connects any two entities. This is the core of the "web" visualization.

```
Relationship
├── from_entity_type    CharField  # 'era' | 'period' | 'person' | 'event'
├── from_entity_id      PositiveIntegerField
├── from_entity         GenericForeignKey
├── to_entity_type      CharField
├── to_entity_id        PositiveIntegerField
├── to_entity           GenericForeignKey
├── relationship_type   CharField choices:
│                         # Person-Person: parent, child, spouse, rival, ally,
│                         #               advisor, subject, influenced
│                         # Person-Event:  participated, caused, was_affected_by,
│                         #               ordered, led, survived
│                         # Event-Event:   caused, followed, prevented, influenced
│                         # Person-Period: ruled, lived_during
│                         # Event-Era:     defined, ended, marked_start_of
├── description         TextField(blank)   # one sentence, shown on connection lines
├── strength            IntegerField(1-5)  # visual weight of edge in graph
├── is_bidirectional    BooleanField       # if True, arrow shown both ways
└── order               PositiveIntegerField
```

**Note on generic relations**: Django's `contenttypes` framework handles polymorphic FK.
For each entity type, there is a ContentType row. `from_entity_type` stores
`'explorer.person'` etc., enabling queries like "all relationships for this person."

Helper methods on each model:
- `Person.get_relationships()` → QuerySet of Relationship where from or to = this person
- `Event.get_causes()` → filter `relationship_type='caused'` where `to_entity=this`
- `Event.get_effects()` → filter `relationship_type='caused'` where `from_entity=this`

---

## URL-to-Model Mapping

| URL pattern | Model | Level |
|-------------|-------|-------|
| `/` | — | 1 (Galaxy) |
| `/explore/<era-slug>/` | Era | 2 |
| `/explore/<era-slug>/period/<period-slug>/` | Period | 2b |
| `/explore/<era-slug>/person/<person-slug>/` | Person | 3 |
| `/explore/<era-slug>/event/<event-slug>/` | Event | 3 |
| `/explore/<era-slug>/connect/<from-slug>/<to-slug>/` | Relationship | 4 |

---

## Cross-Reference Resolution

Body text supports `[[slug]]` syntax. A custom template filter `resolve_links` processes
rendered Markdown HTML, replacing `[[slug]]` patterns with `<a href="...">Name</a>` links.

Resolution order: Person → Event → Period → Era. First match wins.

At render time, unknown slugs emit a `<span class="broken-link">slug</span>` for easy audit.

---

## Admin Strategy

All models are registered in Django Admin with:
- Inline Relationship editing on Person and Event detail pages
- `list_display` showing key fields + status
- `list_filter` on era, status, event_type
- Markdown preview via `markdownx`
- `prepopulated_fields` for slug from name
