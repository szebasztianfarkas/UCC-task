from django.urls import path
from apps.users.views import UserListView, UserDetailView, MeView, ChangePasswordView

urlpatterns = [
    path('',                      UserListView.as_view(),      name='user-list'),
    path('me/',                   MeView.as_view(),            name='user-me'),
    path('me/change-password/',   ChangePasswordView.as_view(), name='user-change-password'),
    path('<int:pk>/',             UserDetailView.as_view(),    name='user-detail'),
]