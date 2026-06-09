import re
import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_MD_EXTENSIONS = ['fenced_code', 'tables', 'nl2br', 'toc']


@register.filter
def markdownify(value):
    if not value:
        return mark_safe('')
    return mark_safe(md.markdown(str(value), extensions=_MD_EXTENSIONS))


@register.filter
def resolve_links(html_content):
    """Replace [[slug]] patterns in rendered HTML with entity hyperlinks."""
    from explorer.models import Person, Event, Period, Era

    def replace_slug(match):
        slug = match.group(1)
        for Model in (Person, Event, Period, Era):
            try:
                entity = Model.objects.get(slug=slug, status='published')
                url = entity.get_absolute_url()
                return (
                    f'<a href="{url}" class="entity-link" data-slug="{slug}">'
                    f'{entity.name}</a>'
                )
            except Model.DoesNotExist:
                continue
        return f'<span class="broken-link" title="Unknown entity: {slug}">{slug}</span>'

    result = re.sub(r'\[\[([a-z0-9-]+)\]\]', replace_slug, str(html_content))
    return mark_safe(result)
