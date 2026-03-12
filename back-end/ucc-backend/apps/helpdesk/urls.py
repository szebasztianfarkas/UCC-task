from django.urls import path
from apps.helpdesk.views import (
    MyChatListView,
    MyActiveChatView,
    ChatDetailView,
    ResolveView,
    RequestAgentView,
    AgentQueueView,
    AgentAssignView,
    AgentResolveView,
    AgentHistoryView,
    MarkReadView,
    UnreadCountsView,
)

urlpatterns = [
    path('my/',                          MyChatListView.as_view(),    name='helpdesk-my-list'),
    path('my/active/',                   MyActiveChatView.as_view(),  name='helpdesk-my-active'),
    path('<int:pk>/',                    ChatDetailView.as_view(),    name='helpdesk-chat'),
    path('<int:pk>/resolve/',            ResolveView.as_view(),       name='helpdesk-resolve'),
    path('<int:pk>/request-agent/',      RequestAgentView.as_view(),  name='helpdesk-request-agent'),
    path('agent/queue/',                 AgentQueueView.as_view(),    name='helpdesk-agent-queue'),
    path('agent/<int:pk>/assign/',       AgentAssignView.as_view(),   name='helpdesk-agent-assign'),
    path('agent/<int:pk>/resolve/',      AgentResolveView.as_view(),  name='helpdesk-agent-resolve'),
    path('agent/history/',               AgentHistoryView.as_view(),  name='helpdesk-agent-history'),
    path('unread-counts/',               UnreadCountsView.as_view(),  name='helpdesk-unread-counts'),
    path('<int:pk>/read/',               MarkReadView.as_view(),      name='helpdesk-mark-read'),
]