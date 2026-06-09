from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from markdownx.models import MarkdownxField


STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published')]


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Era(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=300)
    summary = models.TextField()
    body = MarkdownxField(blank=True)
    featured_image = models.ImageField(upload_to='eras/', blank=True)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    color_accent = models.CharField(max_length=30, default='#8b1a1a')
    icon = models.CharField(max_length=60, blank=True)
    order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('explorer:era_overview', kwargs={'era_slug': self.slug})

    def get_relationships(self):
        ct = ContentType.objects.get_for_model(self)
        return Relationship.objects.filter(
            Q(from_entity_type=ct, from_entity_id=self.pk) |
            Q(to_entity_type=ct, to_entity_id=self.pk)
        )

    class Meta:
        ordering = ['order', 'name']


class Period(models.Model):
    era = models.ForeignKey(Era, on_delete=models.CASCADE, related_name='periods')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.TextField()
    body = MarkdownxField(blank=True)
    featured_image = models.ImageField(upload_to='periods/', blank=True)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return f'{self.era.name} — {self.name}'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('explorer:period_detail', kwargs={
            'era_slug': self.era.slug, 'period_slug': self.slug
        })

    class Meta:
        ordering = ['order', 'start_year']


class Person(models.Model):
    era = models.ForeignKey(Era, on_delete=models.CASCADE, related_name='people')
    period = models.ForeignKey(
        Period, on_delete=models.SET_NULL, null=True, blank=True, related_name='people'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200, blank=True)
    summary = models.TextField()
    body = MarkdownxField(blank=True)
    featured_image = models.ImageField(upload_to='people/', blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    death_year = models.IntegerField(null=True, blank=True)
    reign_start = models.IntegerField(null=True, blank=True)
    reign_end = models.IntegerField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    region = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('explorer:person_detail', kwargs={
            'era_slug': self.era.slug, 'person_slug': self.slug
        })

    def get_relationships(self):
        ct = ContentType.objects.get_for_model(self)
        return Relationship.objects.filter(
            Q(from_entity_type=ct, from_entity_id=self.pk) |
            Q(to_entity_type=ct, to_entity_id=self.pk)
        ).select_related('from_entity_type', 'to_entity_type')

    class Meta:
        ordering = ['reign_start', 'birth_year', 'name']
        verbose_name_plural = 'People'


class Event(models.Model):
    EVENT_TYPES = [
        ('battle', 'Battle'), ('treaty', 'Treaty'), ('revolution', 'Revolution'),
        ('reform', 'Reform'), ('disaster', 'Disaster'), ('cultural', 'Cultural'),
        ('political', 'Political'), ('other', 'Other'),
    ]

    era = models.ForeignKey(Era, on_delete=models.CASCADE, related_name='events')
    period = models.ForeignKey(
        Period, on_delete=models.SET_NULL, null=True, blank=True, related_name='events'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other')
    summary = models.TextField()
    body = MarkdownxField(blank=True)
    featured_image = models.ImageField(upload_to='events/', blank=True)
    year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    region = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f'{self.year}: {self.name}'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('explorer:event_detail', kwargs={
            'era_slug': self.era.slug, 'event_slug': self.slug
        })

    def get_relationships(self):
        ct = ContentType.objects.get_for_model(self)
        return Relationship.objects.filter(
            Q(from_entity_type=ct, from_entity_id=self.pk) |
            Q(to_entity_type=ct, to_entity_id=self.pk)
        ).select_related('from_entity_type', 'to_entity_type')

    def get_causes(self):
        ct = ContentType.objects.get_for_model(self)
        return Relationship.objects.filter(
            relationship_type='caused', to_entity_type=ct, to_entity_id=self.pk
        )

    def get_effects(self):
        ct = ContentType.objects.get_for_model(self)
        return Relationship.objects.filter(
            relationship_type='caused', from_entity_type=ct, from_entity_id=self.pk
        )

    class Meta:
        ordering = ['year', 'name']


class Relationship(models.Model):
    RELATIONSHIP_TYPES = [
        ('parent', 'Parent of'), ('child', 'Child of'), ('spouse', 'Spouse of'),
        ('rival', 'Rival of'), ('ally', 'Ally of'), ('advisor', 'Advisor to'),
        ('subject', 'Subject of'), ('influenced', 'Influenced'),
        ('participated', 'Participated in'), ('caused', 'Caused'),
        ('was_affected_by', 'Was affected by'), ('ordered', 'Ordered'),
        ('led', 'Led'), ('survived', 'Survived'), ('followed', 'Followed'),
        ('prevented', 'Prevented'), ('ruled', 'Ruled during'),
        ('lived_during', 'Lived during'), ('defined', 'Defined'),
        ('ended', 'Ended'), ('marked_start_of', 'Marked start of'),
    ]

    from_entity_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name='outgoing_relationships'
    )
    from_entity_id = models.PositiveIntegerField()
    from_entity = GenericForeignKey('from_entity_type', 'from_entity_id')

    to_entity_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name='incoming_relationships'
    )
    to_entity_id = models.PositiveIntegerField()
    to_entity = GenericForeignKey('to_entity_type', 'to_entity_id')

    relationship_type = models.CharField(max_length=30, choices=RELATIONSHIP_TYPES)
    description = models.TextField(blank=True)
    strength = models.IntegerField(default=3)
    is_bidirectional = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return (
            f'{self.from_entity_type.model}:{self.from_entity_id} '
            f'→ {self.relationship_type} → '
            f'{self.to_entity_type.model}:{self.to_entity_id}'
        )

    class Meta:
        ordering = ['order']
