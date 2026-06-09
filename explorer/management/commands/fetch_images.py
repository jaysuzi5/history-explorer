"""
Management command: fetch_images
Fetches Wikipedia portrait images for Person records that have no featured_image.

Usage:
  uv run python manage.py fetch_images
  uv run python manage.py fetch_images --era romanov-dynasty
  uv run python manage.py fetch_images --overwrite
"""
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from explorer.models import Era, Person

ERA_WIKI_TITLES = {
    "romanov-dynasty": "House of Romanov",
}

WIKI_API = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "HistoryExplorer/1.0 (jaysuzi5@gmail.com)"}

# Hand-tuned Wikipedia article titles per person slug for best image results.
# Falls back to automatic search for any slug not listed here.
WIKI_TITLE_OVERRIDES = {
    "michael-i":    "Michael I of Russia",
    "alexis-i":     "Alexis of Russia",
    "feodor-iii":   "Feodor III of Russia",
    "ivan-v":       "Ivan V of Russia",
    "peter-i":      "Peter the Great",
    "catherine-i":  "Catherine I of Russia",
    "peter-ii":     "Peter II of Russia",
    "anna":         "Anna of Russia",
    "ivan-vi":      "Ivan VI of Russia",
    "elizabeth":    "Elizabeth of Russia",
    "peter-iii":    "Peter III of Russia",
    "catherine-ii": "Catherine the Great",
    "paul-i":       "Paul I of Russia",
    "alexander-i":  "Alexander I of Russia",
    "nicholas-i":   "Nicholas I of Russia",
    "alexander-ii": "Alexander II of Russia",
    "alexander-iii":"Alexander III of Russia",
    "nicholas-ii":  "Nicholas II of Russia",
}


def _wiki_image_url(title, size=800):
    """Return the thumbnail URL for a Wikipedia article title, or None."""
    import httpx
    resp = httpx.get(
        WIKI_API,
        params={
            "action": "query",
            "titles": title,
            "prop": "pageimages",
            "format": "json",
            "pithumbsize": size,
            "pilicense": "any",
            "redirects": 1,
        },
        headers=HEADERS,
        follow_redirects=True,
        timeout=15,
    )
    resp.raise_for_status()
    pages = resp.json().get("query", {}).get("pages", {})
    for page in pages.values():
        thumb = page.get("thumbnail")
        if thumb:
            return thumb.get("source")
    return None


def _search_wiki_title(query):
    """Search Wikipedia and return the top result's title."""
    import httpx
    resp = httpx.get(
        WIKI_API,
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 1,
        },
        headers=HEADERS,
        follow_redirects=True,
        timeout=15,
    )
    resp.raise_for_status()
    results = resp.json().get("query", {}).get("search", [])
    return results[0]["title"] if results else None


def _download_image(url):
    """Download image bytes from URL."""
    import httpx
    resp = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=30)
    resp.raise_for_status()
    ct = resp.headers.get("content-type", "")
    ext = "jpg"
    if "png" in ct:
        ext = "png"
    elif "webp" in ct:
        ext = "webp"
    return resp.content, ext


class Command(BaseCommand):
    help = "Fetch Wikipedia portrait images for persons without a featured_image"

    def add_arguments(self, parser):
        parser.add_argument("--era", help="Only fetch for persons in this era slug")
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Replace images even if already set",
        )

    def _fetch_one(self, obj, slug, upload_to_prefix, wiki_title_map, overwrite):
        """Fetch and save a Wikipedia image for a single model instance."""
        if obj.featured_image and not overwrite:
            return 'skip'
        wiki_title = wiki_title_map.get(slug)
        if not wiki_title:
            return 'skip'
        self.stdout.write(f"  {obj} → «{wiki_title}»")
        try:
            img_url = _wiki_image_url(wiki_title)
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"  Image lookup failed: {exc}"))
            return 'fail'
        if not img_url:
            self.stdout.write(f"  No image found")
            return 'skip'
        try:
            data, ext = _download_image(img_url)
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"  Download failed: {exc}"))
            return 'fail'
        filename = f"{slug}.{ext}"
        obj.featured_image.save(filename, ContentFile(data), save=True)
        self.stdout.write(self.style.SUCCESS(f"  Saved {len(data) // 1024}KB → {filename}"))
        return 'ok'

    def handle(self, *args, **options):
        overwrite = options.get("overwrite", False)

        # Era images
        era_qs = Era.objects.filter(status="published")
        if options.get("era"):
            era_qs = era_qs.filter(slug=options["era"])
        for era in era_qs:
            self._fetch_one(era, era.slug, "eras/", ERA_WIKI_TITLES, overwrite)

        qs = Person.objects.filter(status="published")
        if options.get("era"):
            qs = qs.filter(era__slug=options["era"])
        if not options.get("overwrite"):
            qs = qs.filter(featured_image="")

        total = qs.count()
        self.stdout.write(f"Fetching images for {total} person(s)...")
        ok = skipped = failed = 0

        for person in qs:
            wiki_title = WIKI_TITLE_OVERRIDES.get(person.slug)
            if not wiki_title:
                search_query = f"{person.name} Russia tsar emperor"
                self.stdout.write(f"  Searching Wikipedia: {search_query}")
                try:
                    wiki_title = _search_wiki_title(search_query)
                except Exception as exc:
                    self.stdout.write(self.style.WARNING(f"  Search failed: {exc}"))
                    failed += 1
                    continue
                if not wiki_title:
                    self.stdout.write(f"  No article found for {person.name}")
                    skipped += 1
                    continue

            self.stdout.write(f"  {person.name} → «{wiki_title}»")
            try:
                img_url = _wiki_image_url(wiki_title)
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"  Image lookup failed: {exc}"))
                failed += 1
                continue

            if not img_url:
                self.stdout.write(f"  No image on Wikipedia article")
                skipped += 1
                continue

            try:
                data, ext = _download_image(img_url)
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"  Download failed: {exc}"))
                failed += 1
                continue

            filename = f"{person.slug}.{ext}"
            person.featured_image.save(filename, ContentFile(data), save=True)
            self.stdout.write(
                self.style.SUCCESS(f"  Saved {len(data) // 1024}KB → {filename}")
            )
            ok += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone: {ok} saved, {skipped} skipped (no image), {failed} failed"
        ))
