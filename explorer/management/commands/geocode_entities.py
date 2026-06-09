"""
Management command: geocode_entities
Backfills latitude/longitude/region for Person and Event records.

Uses a curated coordinate table for known slugs (deterministic, no API calls).
For any Event with a `location` string but no curated entry, falls back to the
OpenStreetMap Nominatim geocoder.

Usage:
  uv run python manage.py geocode_entities
  uv run python manage.py geocode_entities --overwrite
  uv run python manage.py geocode_entities --no-nominatim
"""
import time

from django.core.management.base import BaseCommand

from explorer.models import Event, Person

# slug -> (latitude, longitude, region)
COORDS = {
    # ── Romanov Dynasty — people (seat of power) ──
    "michael-i":     (55.7558, 37.6173, "Russia"),   # Moscow
    "alexis-i":      (55.7558, 37.6173, "Russia"),
    "feodor-iii":    (55.7558, 37.6173, "Russia"),
    "ivan-v":        (55.7558, 37.6173, "Russia"),
    "peter-i":       (59.9311, 30.3609, "Russia"),    # St Petersburg (founder)
    "catherine-i":   (59.9311, 30.3609, "Russia"),
    "peter-ii":      (55.7558, 37.6173, "Russia"),    # moved capital back to Moscow
    "anna":          (59.9311, 30.3609, "Russia"),
    "ivan-vi":       (59.9311, 30.3609, "Russia"),
    "elizabeth":     (59.9311, 30.3609, "Russia"),
    "peter-iii":     (59.9311, 30.3609, "Russia"),
    "catherine-ii":  (59.9311, 30.3609, "Russia"),
    "paul-i":        (59.9311, 30.3609, "Russia"),
    "alexander-i":   (59.9311, 30.3609, "Russia"),
    "nicholas-i":    (59.9311, 30.3609, "Russia"),
    "alexander-ii":  (59.9311, 30.3609, "Russia"),
    "alexander-iii": (59.9311, 30.3609, "Russia"),
    "nicholas-ii":   (59.9311, 30.3609, "Russia"),

    # ── French Revolution — people ──
    "louis-xvi":              (48.8049, 2.1204, "France"),   # Versailles
    "marie-antoinette":       (48.8049, 2.1204, "France"),
    "maximilien-robespierre": (48.8566, 2.3522, "France"),   # Paris
    "georges-danton":         (48.8566, 2.3522, "France"),
    "marquis-de-lafayette":   (48.8566, 2.3522, "France"),

    # ── Napoleonic Era — people ──
    "napoleon-bonaparte":       (48.8566, 2.3522, "France"),   # Paris
    "josephine-de-beauharnais": (48.8566, 2.3522, "France"),
    "talleyrand":               (48.8566, 2.3522, "France"),
    "marshal-michel-ney":       (48.8566, 2.3522, "France"),
    "duke-of-wellington":       (51.5074, -0.1278, "Britain"), # London

    # ── French Revolution — events ──
    "bastille-1789":             (48.8532, 2.3692, "France"),   # Bastille, Paris
    "declaration-rights-of-man": (48.8049, 2.1204, "France"),   # Versailles
    "execution-of-louis-xvi":    (48.8656, 2.3212, "France"),   # Place de la Concorde
    "reign-of-terror":           (48.8566, 2.3522, "France"),   # Paris
    "coup-18-brumaire":          (48.8460, 2.2188, "France"),   # Saint-Cloud

    # ── Napoleonic Era — events ──
    "napoleon-crowned-emperor":   (48.8530, 2.3499, "France"),   # Notre-Dame
    "battle-of-trafalgar":        (36.1810, -6.0339, "Iberia"),  # Cape Trafalgar
    "battle-of-austerlitz":       (49.1530, 16.8760, "Central Europe"),
    "invasion-of-russia-1812":    (55.7558, 37.6173, "Russia"),  # Moscow
    "battle-of-borodino":         (55.5200, 35.8200, "Russia"),
    "battle-of-nations-leipzig":  (51.3397, 12.3731, "Central Europe"),
    "hundred-days":               (48.8566, 2.3522, "France"),
    "battle-of-waterloo":         (50.6800, 4.4124, "Low Countries"),
    "congress-of-vienna":         (48.2082, 16.3738, "Central Europe"),
}

NOMINATIM = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "HistoryExplorer/1.0 (jaysuzi5@gmail.com)"}


def _nominatim(query):
    """Geocode a free-text place string via OSM Nominatim. Returns (lat, lng) or None."""
    import httpx
    resp = httpx.get(
        NOMINATIM,
        params={"q": query, "format": "json", "limit": 1},
        headers=HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    results = resp.json()
    if results:
        return float(results[0]["lat"]), float(results[0]["lon"])
    return None


class Command(BaseCommand):
    help = "Backfills latitude/longitude/region for Person and Event records"

    def add_arguments(self, parser):
        parser.add_argument("--overwrite", action="store_true",
                            help="Re-geocode records that already have coordinates")
        parser.add_argument("--no-nominatim", action="store_true",
                            help="Skip Nominatim fallback; use curated table only")

    def handle(self, *args, **options):
        overwrite = options["overwrite"]
        use_nominatim = not options["no_nominatim"]
        saved = skipped = failed = 0

        for model_name, qs in (("Person", Person.objects.all()),
                               ("Event", Event.objects.all())):
            for obj in qs:
                if obj.latitude is not None and not overwrite:
                    continue

                coord = COORDS.get(obj.slug)
                if coord:
                    obj.latitude, obj.longitude, obj.region = coord
                    obj.save(update_fields=["latitude", "longitude", "region"])
                    saved += 1
                    self.stdout.write(f"  {model_name}: {obj.slug} → curated {coord}")
                    continue

                # Fallback: geocode Event.location strings via Nominatim
                location = getattr(obj, "location", "") or ""
                if use_nominatim and location:
                    try:
                        result = _nominatim(location)
                        time.sleep(1)  # Nominatim rate limit: 1 req/sec
                    except Exception as exc:  # network/HTTP error
                        result = None
                        self.stdout.write(self.style.WARNING(
                            f"  {model_name}: {obj.slug} Nominatim error: {exc}"
                        ))
                    if result:
                        obj.latitude, obj.longitude = result
                        obj.save(update_fields=["latitude", "longitude"])
                        saved += 1
                        self.stdout.write(
                            f"  {model_name}: {obj.slug} → Nominatim «{location}» {result}"
                        )
                        continue

                failed += 1
                self.stdout.write(self.style.WARNING(
                    f"  {model_name}: {obj.slug} — no coordinates (skipped)"
                ))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {saved} geocoded, {skipped} already set, {failed} unresolved."
        ))
