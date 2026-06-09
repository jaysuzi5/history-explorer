from django.urls import path
from . import views

app_name = 'explorer'

urlpatterns = [
    path('', views.galaxy, name='galaxy'),
    path('explore/<slug:era_slug>/', views.era_overview, name='era_overview'),
    path('explore/<slug:era_slug>/period/<slug:period_slug>/', views.period_detail, name='period_detail'),
    path('explore/<slug:era_slug>/person/<slug:person_slug>/', views.person_detail, name='person_detail'),
    path('explore/<slug:era_slug>/event/<slug:event_slug>/', views.event_detail, name='event_detail'),
    path('explore/<slug:era_slug>/connect/<slug:from_slug>/<slug:to_slug>/', views.connection_detail, name='connection_detail'),
]
