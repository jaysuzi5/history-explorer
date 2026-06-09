from django.contrib import admin
from .models import Tag, Era, Period, Person, Event, Relationship


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Era)
class EraAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_year', 'end_year', 'order', 'status']
    list_filter = ['status']
    list_editable = ['order', 'status']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = [
        (None, {'fields': ['name', 'slug', 'tagline', 'status', 'order']}),
        ('Dates & Theme', {'fields': ['start_year', 'end_year', 'color_accent', 'icon']}),
        ('Content', {'fields': ['summary', 'body', 'featured_image']}),
    ]


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'era', 'start_year', 'end_year', 'order', 'status']
    list_filter = ['era', 'status']
    list_editable = ['order', 'status']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'era', 'period', 'reign_start', 'reign_end', 'status']
    list_filter = ['era', 'period', 'status']
    list_editable = ['status']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['tags']
    fieldsets = [
        (None, {'fields': ['era', 'period', 'name', 'slug', 'title', 'nationality', 'status']}),
        ('Dates', {'fields': ['birth_year', 'death_year', 'reign_start', 'reign_end']}),
        ('Content', {'fields': ['summary', 'body', 'featured_image']}),
        ('Meta', {'fields': ['tags', 'metadata']}),
    ]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'end_year', 'event_type', 'era', 'period', 'status']
    list_filter = ['era', 'period', 'event_type', 'status']
    list_editable = ['status']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['tags']
    fieldsets = [
        (None, {'fields': ['era', 'period', 'name', 'slug', 'event_type', 'status']}),
        ('Dates & Location', {'fields': ['year', 'end_year', 'location']}),
        ('Content', {'fields': ['summary', 'body', 'featured_image']}),
        ('Meta', {'fields': ['tags', 'metadata']}),
    ]


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = [
        'from_entity_type', 'from_entity_id', 'relationship_type',
        'to_entity_type', 'to_entity_id', 'strength', 'is_bidirectional',
    ]
    list_filter = ['relationship_type', 'from_entity_type', 'to_entity_type']
    fields = [
        'from_entity_type', 'from_entity_id',
        'to_entity_type', 'to_entity_id',
        'relationship_type', 'description', 'strength', 'is_bidirectional', 'order',
    ]
