# History Explorer — Implementation Plan

Stack mirrors unscripted-living: Django 6.0, PostgreSQL, Bootstrap 5, WhiteNoise, markdownx, UV, Docker + k8s.

---

## Phase 1 — Project Setup ✅ MVP
- [x] `pyproject.toml` with matching dependencies
- [x] `config/` package: settings, urls, wsgi, asgi
- [x] `explorer/` Django app scaffolding
- [x] `.env.example`, `.gitignore`, `Dockerfile`
- [x] `manage.py`

**Dev setup:**
```bash
cd history-explorer
uv sync
cp .env.example .env   # fill in DB credentials
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver localhost:8001
```

---

## Phase 2 — Data Models ✅ MVP
- [x] `Tag`, `Era`, `Period`, `Person`, `Event` models
- [x] `Relationship` model using Django `contenttypes` GenericFK
- [x] Initial migration `0001_initial.py`
- [x] Django admin with list_display, list_filter, prepopulated slugs

**Key design:**
- All body fields use `MarkdownxField` (markdownx)
- `Relationship` uses two GenericForeignKeys: `from_entity` + `to_entity`
- `[[slug]]` cross-references resolved at render time by `resolve_links` template tag

---

## Phase 3 — Views & URL Routing ✅ MVP
- [x] Level 1: `galaxy` (landing)
- [x] Level 2: `era_overview` + `period_detail`
- [x] Level 3: `person_detail`, `event_detail`
- [x] Level 4: `connection_detail`
- [x] `build_graph_data_for_era()` + `build_graph_data_for_entity()`
- [x] `build_timeline_data()` for vis-timeline JSON

---

## Phase 4 — Templates & CSS ✅ MVP
- [x] `base.html` — dark heritage theme, Bootstrap 5, Cinzel+Lora+Inter fonts
- [x] `galaxy.html` — era card grid
- [x] `era_overview.html` — hero + vis-timeline + entity grids + Cytoscape graph
- [x] `person_detail.html` + `event_detail.html` — two-column, quick facts, body, relationships
- [x] `connection_detail.html` — mini graph + relationship description
- [x] `_breadcrumb.html` partial
- [x] `static/css/site.css` — heritage CSS variables, layout, vis-timeline dark overrides

**CDN libs (no build pipeline):**
- Cytoscape.js 3.x
- vis-timeline 7.x
- Bootstrap 5.3.3
- Bootstrap Icons 1.11.3

---

## Phase 5 — Template Tags ✅ MVP
- [x] `resolve_links` filter: `[[slug]]` → `<a href="...">Name</a>`, unknown slugs → `<span class="broken-link">`

---

## Phase 6 — Seed Data (Romanov Prototype)
- [ ] Django fixture `explorer/fixtures/romanov.json`
- [ ] ~5 sub-periods, 16 Tsars/Tsarinas, 10+ key figures, 20 events
- [ ] ~50 Relationship records (succession, marriage, conflict, alliance, influence)
- Load: `uv run python manage.py loaddata romanov`

---

## Phase 7 — Infrastructure
- [ ] `k8s/deployment.yaml` — mirrors unscripted-living pattern, app=history-explorer, namespace=history-explorer
- [ ] `k8s/secrets.yaml` — SealedSecret for DB creds + secret_key
- [ ] Cloudflare tunnel route: `history.jaycurtis.org` → service:80
- [ ] Multi-arch Docker build + push

**Build & deploy:**
```bash
uv lock
docker buildx build --platform linux/amd64,linux/arm64 \
  -t jaysuzi5/history-explorer:latest --push .
kubectl apply -f k8s/
kubectl rollout restart deployment history-explorer -n history-explorer
```

---

## Phase 8 — Search
- [ ] Global search view across `Person.name`, `Event.name`, `Era.name`
- [ ] Results grouped by type with breadcrumb context
- [ ] Search bar in navbar

---

## Phase 9 — Polish
- [ ] Hover popovers on `entity-link` anchors (Bootstrap Popover with name + summary)
- [ ] `prefers-reduced-motion` media query to disable Cytoscape + vis-timeline animations
- [ ] Screen-reader fallback: visually-hidden `<ul>` listing all graph nodes
- [ ] Mobile: timeline vertical scroll, graph tap-to-explore on small screens
- [ ] Graph state persistence via `sessionStorage` key `graph-state-<era-slug>`

---

## Phase 10 — OpenTelemetry
- [ ] Add `otel_config.py` matching unscripted-living pattern
- [ ] Wire into `wsgi.py` + `asgi.py`
- [ ] Add OTEL env vars to k8s deployment manifest
