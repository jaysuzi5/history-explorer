# History Explorer — Project Overview

## Vision

An interactive web application for exploring historical periods, figures, and events through
visual relationship maps and hierarchical drill-down. The explorer presents history as a
connected web rather than a flat list — every person, event, and period links to what
influenced it and what it influenced.

The initial prototype covers the **Romanov Dynasty (1613–1917)**: its Tsars, major events,
and the causal threads connecting them.

---

## Core User Experience

### Levels of Exploration

The site is organized into four levels. Each level is richer and more detailed than the one
above it. Users can move freely between levels using breadcrumbs, back buttons, and
in-content hyperlinks.

| Level | Name | What the user sees |
|-------|------|--------------------|
| 1 | **Galaxy** | Cards for each historical era/dynasty on the landing page |
| 2 | **Era Overview** | Hero banner + interactive timeline + relationship graph for one era |
| 3 | **Entity Detail** | Full page for a person, event, or period within the era |
| 4 | **Connection Detail** | Focused view of the relationship between two entities |

### Navigation Principles

- **Drill down**: click any card, node, or link to go deeper
- **Breadcrumb trail**: always visible; shows the path back to the top
- **In-content links**: rich descriptions mention people/events as clickable links
- **Relationship graph**: always shows the current entity's connections; click any node to jump
- **Back navigation**: browser back works; era-level back button takes user to parent era/period

### Visual Language

- Level 1 (Galaxy): large illustrated cards, minimal text, dramatic full-bleed images
- Level 2 (Era): dark themed, rich color, horizontal timeline + force-directed relationship graph
- Level 3 (Entity): two-column layout — portrait/image left, rich text right; connection panel below
- Level 4 (Connection): small focused diagram + annotation

---

## Initial Content: Romanov Dynasty Prototype

See `documents/prototype-romanov.md` for the seeded data plan.

Key entities in the prototype:

- **Persons**: ~16 Tsars/Tsarinas from Michael I to Nicholas II, plus key figures
  (Rasputin, Lenin, Pugachev, Napoleon, etc.)
- **Events**: ~20 major events including the Time of Troubles end, Great Northern War,
  Emancipation of Serfs, 1905 Revolution, WWI, February/October Revolutions
- **Periods**: sub-periods within the dynasty (Early Romanovs, Petrine Era, Catherine's Age,
  19th Century Reform Era, Final Romanovs)
- **Relationships**: succession, marriage, conflict, alliance, influence

---

## Success Criteria

1. User can navigate from the landing page to full detail on Nicholas II in ≤3 clicks
2. Relationship graph shows first-degree connections for any entity
3. In-text links between entities work bidirectionally
4. Breadcrumb trail is accurate at every level
5. Mobile-responsive layout at all four levels
6. Dark mode supported (inherits Bootstrap 5 `data-bs-theme`)
