from django.urls import path
from .views import FontListView, FontCreateView, FontDeleteView

urlpatterns = [
    path('organizer/<str:organizer>/fonts/', FontListView.as_view(), name='list'),
    path('organizer/<str:organizer>/fonts/add/', FontCreateView.as_view(), name='add'),
    path('organizer/<str:organizer>/fonts/<int:pk>/delete/', FontDeleteView.as_view(), name='delete'),
]
