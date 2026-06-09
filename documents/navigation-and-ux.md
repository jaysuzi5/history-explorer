# History Explorer — Navigation & UX Design

## Navigation Mental Model

The explorer behaves like a "zoomable map of history." The user starts at altitude, sees
the full landscape, then zooms into regions, then into specific locations. At every zoom
level they can see where they came from and what surrounds them.

There are three independent navigation mechanisms, all operating simultaneously:

1. **Hierarchical breadcrumb** — the "where am I?" trail
2. **Relationship graph** — the "what connects to this?" spider web
3. **In-content links** — the "while reading, jump to this" path

---

## Level 1: Galaxy (Landing Page `/`)

### Layout
- Full-viewport hero section: site title + tagline
- Era cards below: large illustrated cards (≥400px tall), one per historical era
- Each card shows: era name, date range, tagline, dominant color accent, and a compelling
  background image

### Interaction
- Hover: card lifts, overlay fades in with summary text
- Click: navigate to Era Overview (`/explore/<era-slug>/`)

### Navigation state
- No breadcrumb needed at root level
- No graph (no single entity to graph)

---

## Level 2: Era Overview (`/explore/<era-slug>/`)

### Layout

```
┌─────────────────────────────────────────────────────┐
│  HERO BANNER (era image + name + date range)         │
│  Breadcrumb: Home > Romanov Dynasty                  │
├─────────────────────────────────────────────────────┤
│  SUMMARY TEXT (2-3 paragraphs, era introduction)    │
├─────────────────────────────────────────────────────┤
│  INTERACTIVE TIMELINE                                │
│  Horizontal scroll, Tsars/events as nodes on a line │
│  Color-coded: persons=gold, events=red, periods=blue │
├──────────────────────────┬──────────────────────────┤
│  KEY FIGURES             │  KEY EVENTS               │
│  Card grid (3 col)       │  Card grid (3 col)        │
│  Portrait + name + dates │  Year + title + summary   │
├─────────────────────────────────────────────────────┤
│  RELATIONSHIP GRAPH (full width)                     │
│  Force-directed; all persons + events as nodes      │
│  Edges show relationship type                        │
└─────────────────────────────────────────────────────┘
```

### Timeline Component

- Library: **vis-timeline** (CDN)
- Two groups: "Rulers" and "Events"
- Clicking a timeline item opens a tooltip with name/summary + "View Details" button
- Overlapping events shown stacked
- Keyboard: arrow keys scroll timeline; Escape closes tooltip

### Relationship Graph Component

- Library: **Cytoscape.js** (CDN)
- Nodes: circular, sized by `strength` (importance score computed from relationship count)
- Edges: labeled with relationship type, thickness = strength
- Colors: persons=gold (#c9a84c), events=crimson (#8b1a1a), periods=navy (#1a3a6b)
- Interactions:
  - Click node → navigate to entity detail page
  - Hover node → tooltip with name + summary
  - Double-click node → expand to show its second-degree connections
  - Pan + zoom with mouse/trackpad
  - "Focus on" button centers and zooms to selected node

### Sub-Periods Panel

If the era has defined sub-periods, show a horizontal row of period cards between the
timeline and the figure/event grids. Clicking a period card filters the grids below to
show only entities within that period.

---

## Level 3: Entity Detail (`/explore/<era>/person/<slug>/` or `/event/<slug>/`)

### Common Layout (Person and Event share structure)

```
┌─────────────────────────────────────────────────────┐
│  Breadcrumb: Home > Romanov Dynasty > Nicholas II   │
│  Back button: "← Back to Romanov Dynasty"           │
├───────────────────────┬─────────────────────────────┤
│  PORTRAIT / IMAGE     │  NAME + TITLE/TYPE          │
│  (left column, 1/3)   │  DATE RANGE                 │
│                       │  SUMMARY (bold intro)       │
│  QUICK FACTS panel:   │                             │
│  - born/died          │  BODY TEXT                  │
│  - reign dates        │  (Markdown, full biography/ │
│  - era / period       │   event description)        │
│  - type/nationality   │  [[slug]] links resolved    │
├───────────────────────┴─────────────────────────────┤
│  RELATIONSHIPS PANEL (full width)                   │
│  Tab strip: All | Family | Events | Influences      │
│  Two modes: "Graph view" toggle / "List view"       │
│  Graph: mini Cytoscape focused on this entity       │
│  List: categorized rows with link + description     │
├─────────────────────────────────────────────────────┤
│  TIMELINE STRIP (full width, narrow)                │
│  Shows this entity's position within the era        │
│  Highlights their dates; other entities shown faded │
├─────────────────────────────────────────────────────┤
│  RELATED ENTITIES (card row)                        │
│  "Others who were connected to this person/event"   │
│  3-6 cards, same card style as Level 2 grids        │
└─────────────────────────────────────────────────────┘
```

### Body Text Cross-Links

- `[[nicholas-ii]]` in Markdown → rendered as `<a href="/explore/romanov/person/nicholas-ii/">Nicholas II</a>`
- On hover: a popover card showing name + summary (no page navigation required)
- "Already visited" links shown in a different color (CSS `:visited`)

### Person-Specific Additions
- Quick Facts: birth year, death year, reign dates, successor/predecessor links
- Relationships grouped: Family Tree (spouse, children, parents), Political (allies, rivals), Influenced By/Influenced

### Event-Specific Additions
- Quick Facts: year, location, event type, era, period
- Relationships grouped: Causes (what caused this), Effects (what this caused), Participants (persons involved)

---

## Level 4: Connection Detail (`/explore/<era>/connect/<from-slug>/<to-slug>/`)

### Layout

```
┌─────────────────────────────────────────────────────┐
│  Breadcrumb: Home > Romanov > Nicholas II           │
│  "Relationship: Nicholas II ↔ Russo-Japanese War"   │
├──────────────────┬──────────────────────────────────┤
│  Entity A card   │   Connection diagram (mini graph)│
│                  │   Just these two nodes + edge    │
│  Entity B card   │   with labeled relationship      │
├─────────────────────────────────────────────────────┤
│  RELATIONSHIP DESCRIPTION                           │
│  Longer text explaining the relationship            │
│  Both entity names link back to their detail pages  │
└─────────────────────────────────────────────────────┘
```

This level is optional — reached only if a Relationship object has a non-empty `description`
field. Otherwise clicking an edge in the graph navigates directly to the target entity.

---

## Breadcrumb Implementation

Breadcrumb context is injected via a context processor. Each view pushes its "trail" onto
a `breadcrumbs` list:

```python
# Person detail view — breadcrumbs
[
    {"label": "Home",             "url": "/"},
    {"label": "Romanov Dynasty",  "url": "/explore/romanov-dynasty/"},
    {"label": "Nicholas II",      "url": None}  # current page, no link
]
```

Template partial `_breadcrumb.html` renders this list.

---

## Graph State Persistence

When a user navigates from the Era Overview graph to an entity and back, the graph returns
to the same pan/zoom state using `sessionStorage`. Key: `graph-state-<era-slug>`.

---

## Search

A global search bar (navbar) runs a full-text query across Person.name, Event.name,
and Era.name. Results page groups hits by type (Eras / People / Events) and shows
breadcrumb context for each hit ("in Romanov Dynasty").

---

## Mobile Considerations

- Level 1: cards stack vertically, full width
- Level 2: timeline becomes vertically scrollable; graph becomes a tap-to-explore
  panel (initial zoom shows only top 10 nodes by importance)
- Level 3: two columns collapse to single column; portrait above text
- Relationship list view is default on mobile (graph view opt-in)
