# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

MVP implemented. Running Django app with all models, views, and templates. See `plan.md` for remaining phases.

## Dev Commands

```bash
uv sync                                       # install deps (creates uv.lock on first run)
cp .env.example .env                          # fill in POSTGRES_* + SECRET_KEY
uv run python manage.py migrate               # apply migrations
uv run python manage.py createsuperuser       # create admin user
uv run python manage.py runserver localhost:8001
```

## Stack

- **Backend**: Django + `markdownx` for body fields, `contenttypes` framework for polymorphic Relationship FK
- **Frontend**: Bootstrap 5, Cytoscape.js 3.x (CDN), vis-timeline 7.x (CDN), GLightbox (CDN) — no npm build pipeline
- **Typography**: Cinzel (headings), Lora (body), Inter (UI chrome) — Google Fonts

## Project Layout

```
config/          Django project config (settings, urls, wsgi, asgi)
explorer/        Main app: models, views, urls, admin, template tags
  migrations/    Initial migration (0001_initial.py)
  templatetags/  explorer_tags.py — resolve_links filter
templates/       base.html + explorer/* (galaxy, era_overview, person/event detail, etc.)
static/css/      site.css — heritage dark theme, vis-timeline overrides
documents/       Design specs (overview, data-model, navigation-and-ux, visualization)
plan.md          Full implementation roadmap with phase checklist
```

## Architecture

Four-level explorer: Galaxy (landing) → Era → Entity (Person/Event) → Connection.

### Data Model

All content models (Era, Period, Person, Event) share: `slug`, `summary`, `body` (MarkdownxField), `featured_image`, `status`, `metadata` (JSONField).

`Relationship` uses Django's `contenttypes` generic FK to connect any two entities. `from_entity_type` stores `'explorer.person'` etc. Key helper methods: `Person.get_relationships()`, `Event.get_causes()`, `Event.get_effects()`.

Body text uses `[[slug]]` cross-references resolved at render time by a `resolve_links` template filter. Resolution order: Person → Event → Period → Era. Unknown slugs emit `<span class="broken-link">`.

### URL Structure

```
/                                               # Level 1: Galaxy
/explore/<era-slug>/                            # Level 2: Era Overview
/explore/<era-slug>/period/<period-slug>/       # Level 2b: Period
/explore/<era-slug>/person/<person-slug>/       # Level 3: Person
/explore/<era-slug>/event/<event-slug>/         # Level 3: Event
/explore/<era-slug>/connect/<from>/<to>/        # Level 4: Connection
```

### Graph Data

Views build graph JSON via a `build_graph_data(entity)` helper that serializes published Relationship querysets. Injected into pages as `<script id="graph-data" type="application/json">`. Graph state (pan/zoom) persisted in `sessionStorage` under key `graph-state-<era-slug>`.

Cytoscape layout: `cose` (force-directed) for Era Overview; `concentric` (entity at center) for Entity Detail.

### Visual Theme

CSS custom properties defined in `site.css`:
- `--he-gold: #c9a84c` (persons), `--he-crimson: #8b1a1a` (events), `--he-navy: #1a3a6b` (periods)
- Each Era has `color_accent` applied as `--era-accent` on `<body>` for per-era theming
- Cytoscape node colors match: persons=gold circles, events=crimson diamonds, periods=navy rounded-rectangles

### Breadcrumbs

Injected via context processor as `breadcrumbs` list — each item `{label, url}` with `url=None` for current page. Template partial `_breadcrumb.html`.

## Design Docs

- `documents/overview.md` — vision, UX levels, success criteria
- `documents/data-model.md` — full model field specs, admin strategy
- `documents/navigation-and-ux.md` — per-level layout specs, component interactions
- `documents/visualization.md` — Cytoscape/vis-timeline schemas, CSS variables, accessibility
