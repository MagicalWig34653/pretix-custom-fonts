from django.urls import path
from .views import FontListView, FontCreateView, FontDeleteView, EventFontSettingsView

urlpatterns = [
    path('control/organizer/<str:organizer>/fonts/', FontListView.as_view(), name='list'),
    path('control/organizer/<str:organizer>/fonts/add/', FontCreateView.as_view(), name='add'),
    path('control/organizer/<str:organizer>/fonts/<int:pk>/delete/', FontDeleteView.as_view(), name='delete'),
    path('control/event/<str:organizer>/<str:event>/fonts/settings/', EventFontSettingsView.as_view(), name='event_settings'),
]
