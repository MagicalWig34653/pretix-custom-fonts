from django.urls import path
from .views import FontListView, FontCreateView, FontDeleteView, FontUpdateView

urlpatterns = [
    path('control/organizer/<str:organizer>/fonts/', FontListView.as_view(), name='list'),
    path('control/organizer/<str:organizer>/fonts/add/', FontCreateView.as_view(), name='add'),
    path('control/organizer/<str:organizer>/fonts/<int:pk>/edit/', FontUpdateView.as_view(), name='edit'),
    path('control/organizer/<str:organizer>/fonts/<int:pk>/delete/', FontDeleteView.as_view(), name='delete'),
]
