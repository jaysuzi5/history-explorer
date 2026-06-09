from django.db import migrations, models
import django.db.models.deletion
import markdownx.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Era',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('tagline', models.CharField(max_length=300)),
                ('summary', models.TextField()),
                ('body', markdownx.models.MarkdownxField(blank=True)),
                ('featured_image', models.ImageField(blank=True, upload_to='eras/')),
                ('start_year', models.IntegerField()),
                ('end_year', models.IntegerField(blank=True, null=True)),
                ('color_accent', models.CharField(default='#8b1a1a', max_length=30)),
                ('icon', models.CharField(blank=True, max_length=60)),
                ('order', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(
                    choices=[('draft', 'Draft'), ('published', 'Published')],
                    default='draft', max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['order', 'name']},
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('summary', models.TextField()),
                ('body', markdownx.models.MarkdownxField(blank=True)),
                ('featured_image', models.ImageField(blank=True, upload_to='periods/')),
                ('start_year', models.IntegerField()),
                ('end_year', models.IntegerField(blank=True, null=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(
                    choices=[('draft', 'Draft'), ('published', 'Published')],
                    default='draft', max_length=20,
                )),
                ('era', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='periods', to='explorer.era',
                )),
            ],
            options={'ordering': ['order', 'start_year']},
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('summary', models.TextField()),
                ('body', markdownx.models.MarkdownxField(blank=True)),
                ('featured_image', models.ImageField(blank=True, upload_to='people/')),
                ('birth_year', models.IntegerField(blank=True, null=True)),
                ('death_year', models.IntegerField(blank=True, null=True)),
                ('reign_start', models.IntegerField(blank=True, null=True)),
                ('reign_end', models.IntegerField(blank=True, null=True)),
                ('nationality', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(
                    choices=[('draft', 'Draft'), ('published', 'Published')],
                    default='draft', max_length=20,
                )),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('era', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='people', to='explorer.era',
                )),
                ('period', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='people', to='explorer.period',
                )),
                ('tags', models.ManyToManyField(blank=True, to='explorer.tag')),
            ],
            options={
                'verbose_name_plural': 'People',
                'ordering': ['reign_start', 'birth_year', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('event_type', models.CharField(
                    choices=[
                        ('battle', 'Battle'), ('treaty', 'Treaty'),
                        ('revolution', 'Revolution'), ('reform', 'Reform'),
                        ('disaster', 'Disaster'), ('cultural', 'Cultural'),
                        ('political', 'Political'), ('other', 'Other'),
                    ],
                    default='other', max_length=20,
                )),
                ('summary', models.TextField()),
                ('body', markdownx.models.MarkdownxField(blank=True)),
                ('featured_image', models.ImageField(blank=True, upload_to='events/')),
                ('year', models.IntegerField()),
                ('end_year', models.IntegerField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=200)),
                ('status', models.CharField(
                    choices=[('draft', 'Draft'), ('published', 'Published')],
                    default='draft', max_length=20,
                )),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('era', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='events', to='explorer.era',
                )),
                ('period', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='events', to='explorer.period',
                )),
                ('tags', models.ManyToManyField(blank=True, to='explorer.tag')),
            ],
            options={'ordering': ['year', 'name']},
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_entity_id', models.PositiveIntegerField()),
                ('to_entity_id', models.PositiveIntegerField()),
                ('relationship_type', models.CharField(
                    choices=[
                        ('parent', 'Parent of'), ('child', 'Child of'), ('spouse', 'Spouse of'),
                        ('rival', 'Rival of'), ('ally', 'Ally of'), ('advisor', 'Advisor to'),
                        ('subject', 'Subject of'), ('influenced', 'Influenced'),
                        ('participated', 'Participated in'), ('caused', 'Caused'),
                        ('was_affected_by', 'Was affected by'), ('ordered', 'Ordered'),
                        ('led', 'Led'), ('survived', 'Survived'), ('followed', 'Followed'),
                        ('prevented', 'Prevented'), ('ruled', 'Ruled during'),
                        ('lived_during', 'Lived during'), ('defined', 'Defined'),
                        ('ended', 'Ended'), ('marked_start_of', 'Marked start of'),
                    ],
                    max_length=30,
                )),
                ('description', models.TextField(blank=True)),
                ('strength', models.IntegerField(default=3)),
                ('is_bidirectional', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(default=0)),
                ('from_entity_type', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='outgoing_relationships',
                    to='contenttypes.contenttype',
                )),
                ('to_entity_type', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='incoming_relationships',
                    to='contenttypes.contenttype',
                )),
            ],
            options={'ordering': ['order']},
        ),
    ]
