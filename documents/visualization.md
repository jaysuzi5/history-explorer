# History Explorer — Visualization Design

## Libraries

| Purpose | Library | Delivery |
|---------|---------|---------|
| Relationship graph | Cytoscape.js 3.x | CDN |
| Timeline | vis-timeline 7.x | CDN |
| Popover cards (hover preview) | Bootstrap 5 Popovers | already in stack |
| Image lightbox | GLightbox (same as unscripted-living) | CDN |

No npm build pipeline. All JS loaded from CDN, same pattern as unscripted-living.

---

## Cytoscape.js — Relationship Graph

### Node Schema

```javascript
{
  data: {
    id: 'person-nicholas-ii',
    label: 'Nicholas II',
    type: 'person',          // 'person' | 'event' | 'period' | 'era'
    url: '/explore/romanov-dynasty/person/nicholas-ii/',
    summary: 'Last Tsar of Russia...',
    importance: 8,           // 1-10, drives node size
    imageUrl: '/media/...'   // optional, used for node background-image
  }
}
```

### Edge Schema

```javascript
{
  data: {
    id: 'rel-nicholas-russo-japanese',
    source: 'person-nicholas-ii',
    target: 'event-russo-japanese-war',
    label: 'ordered',
    strength: 4,             // 1-5, drives edge thickness
    url: null                // or '/explore/.../connect/.../' if Level 4 exists
  }
}
```

### Styles

```javascript
const style = [
  {
    selector: 'node[type="person"]',
    style: {
      'background-color': '#c9a84c',
      'border-color': '#8a6a1e',
      'label': 'data(label)',
      'font-size': '11px',
      'color': '#f0e6c8',
      'width': 'mapData(importance, 1, 10, 30, 80)',
      'height': 'mapData(importance, 1, 10, 30, 80)',
    }
  },
  {
    selector: 'node[type="event"]',
    style: {
      'background-color': '#8b1a1a',
      'border-color': '#5a0f0f',
      'shape': 'diamond',
      'color': '#f0e6c8',
    }
  },
  {
    selector: 'node[type="period"]',
    style: {
      'background-color': '#1a3a6b',
      'shape': 'roundrectangle',
    }
  },
  {
    selector: 'node:selected',
    style: {
      'border-width': 3,
      'border-color': '#ffffff',
    }
  },
  {
    selector: 'edge',
    style: {
      'width': 'mapData(strength, 1, 5, 1, 4)',
      'line-color': '#555',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'label': 'data(label)',
      'font-size': '9px',
      'color': '#aaa',
    }
  }
]
```

### Layout

- Era overview (large graph, many nodes): `layout: { name: 'cose', animate: true }`
  (CoSE = physics-based force-directed, good for dense graphs)
- Entity detail (small focused graph): `layout: { name: 'concentric' }`
  (target entity at center, relationships in rings by type)

### Event Handling

```javascript
cy.on('tap', 'node', function(evt) {
  const url = evt.target.data('url');
  if (url) window.location.href = url;
});

cy.on('mouseover', 'node', function(evt) {
  showTooltip(evt.target.data('label'), evt.target.data('summary'), evt);
});

cy.on('tap', 'edge', function(evt) {
  const url = evt.target.data('url');
  if (url) window.location.href = url;
  // else: show edge label in a toast
});
```

### Data Loading

Graph data is injected into the page as a JSON `<script>` block by the Django view:

```html
<script id="graph-data" type="application/json">
  {{ graph_json|safe }}
</script>
```

Django view builds the graph JSON from the Relationship queryset, serializing only
published entities. The view helper `build_graph_data(entity)` accepts any model instance
and returns `{nodes: [...], edges: [...]}`.

---

## vis-timeline — Era Timeline

### Groups

```javascript
const groups = [
  { id: 'rulers', content: 'Rulers', className: 'group-rulers' },
  { id: 'events', content: 'Events', className: 'group-events' },
  { id: 'periods', content: 'Periods', className: 'group-periods' },
]
```

### Item Types

| Source model | vis item type | display |
|-------------|--------------|---------|
| Person (with reign dates) | `range` | spans entire reign |
| Event (single year) | `point` | dot on the line |
| Event (multi-year) | `range` | spans duration |
| Period | `background` | shaded region behind all items |

### Configuration

```javascript
const options = {
  stack: true,
  start: 1600,
  end: 1920,
  zoomMin: 1000 * 60 * 60 * 24 * 365 * 5,   // 5 years
  zoomMax: 1000 * 60 * 60 * 24 * 365 * 400,  // 400 years
  orientation: { axis: 'top' },
  tooltip: { followMouse: true },
}
```

### Interaction

- Click item → navigates to entity detail
- Hover → Bootstrap popover with name + summary
- The timeline is the "map" of the era; the graph is the "web" of connections

---

## Visual Theme — Heritage/Cartographic

The site uses a dark, rich visual language inspired by aged maps, illuminated manuscripts,
and imperial portraiture — contrasting with the clean modern UI of unscripted-living.

### CSS Custom Properties (site.css additions)

```css
:root {
  --he-gold:        #c9a84c;
  --he-gold-light:  #e8d08a;
  --he-crimson:     #8b1a1a;
  --he-navy:        #1a2a4a;
  --he-parchment:   #f5f0e8;
  --he-ink:         #1a1a2e;
  --he-accent:      var(--he-gold);
}

[data-bs-theme="dark"] {
  --he-bg:          #0f0f1a;
  --he-surface:     #1a1a2e;
  --he-text:        #e8d08a;
}
```

### Typography

- Headings: `Cinzel` (Google Fonts) — classical serif, Roman-inspired, appropriate for
  imperial history
- Body: `Lora` (already in stack via unscripted-living) — readable serif
- UI chrome: `Inter` (already in stack) — clean sans for nav, breadcrumbs, labels

### Era Color Accents

Each Era has a `color_accent` field used to theme its pages:
- Romanov: `#8b1a1a` (deep imperial crimson)
- Applied as CSS custom property `--era-accent` on `<body>` or `<main>` element
- Used for: hero gradient overlay, timeline highlights, active breadcrumb, focus rings

---

## Accessibility

- All graph nodes are also listed in a visually-hidden `<ul>` for screen readers
- Timeline is supplemented by a date-sorted `<table>` accessible to screen readers
- Color is never the only differentiator (node shape also encodes type)
- `prefers-reduced-motion`: disable Cytoscape animations, vis-timeline easing
