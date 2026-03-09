from django.urls import path
from apps.events.views import EventListView, EventDetailView, EventJoinView, EventLeaveView

urlpatterns = [
    path('',            EventListView.as_view(),   name='event-list'),
    path('<int:pk>/',   EventDetailView.as_view(),  name='event-detail'),
    path('<int:pk>/join/',  EventJoinView.as_view(),  name='event-join'),
    path('<int:pk>/leave/', EventLeaveView.as_view(), name='event-leave'),
]