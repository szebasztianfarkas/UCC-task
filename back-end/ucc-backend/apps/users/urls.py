from django.urls import path
from apps.users.views import (
    UserListView,
    UserDetailView,
    MeView,
    ChangePasswordView,
    EmailChangeInitiateView,
    EmailChangeConfirmView,
)

urlpatterns = [
    path('',                       UserListView.as_view(),            name='user-list'),
    path('me/',                    MeView.as_view(),                  name='user-me'),
    path('me/change-password/',    ChangePasswordView.as_view(),      name='user-change-password'),
    path('me/email/initiate/',     EmailChangeInitiateView.as_view(), name='user-email-initiate'),
    path('me/email/confirm/',      EmailChangeConfirmView.as_view(),  name='user-email-confirm'),
    path('<int:pk>/',              UserDetailView.as_view(),          name='user-detail'),
]