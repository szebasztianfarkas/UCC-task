from django.db import models
from django.conf import settings


class HelpdeskChat(models.Model):
    OPEN       = 'open'
    WAITING    = 'waiting'
    AGENT_OPEN = 'agent_open'
    RESOLVED   = 'resolved'
    LOCKED     = 'locked'

    STATUS_CHOICES = [
        (OPEN,       'Open'),
        (WAITING,    'Waiting for agent'),
        (AGENT_OPEN, 'With agent'),
        (RESOLVED,   'Resolved'),
        (LOCKED,     'Locked'),
    ]

    CLOSED_STATUSES = {RESOLVED, LOCKED}

    user          = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='helpdesk_chats',
    )
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_helpdesk_chats',
    )
    status        = models.CharField(max_length=16, choices=STATUS_CHOICES, default=OPEN)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    @property
    def is_closed(self):
        return self.status in self.CLOSED_STATUSES

    @property
    def is_locked(self):
        return self.status == self.LOCKED

    def __str__(self):
        return f'Chat #{self.pk} for {self.user} ({self.status})'


class HelpdeskMessage(models.Model):
    BOT       = 'bot'
    USER      = 'user'
    AGENT     = 'agent'
    SYSTEM    = 'system'
    ROLE_CHOICES = [
        (BOT,    'Bot'),
        (USER,   'User'),
        (AGENT,  'Agent'),
        (SYSTEM, 'System'),
    ]

    chat       = models.ForeignKey(
        HelpdeskChat,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role       = models.CharField(max_length=8, choices=ROLE_CHOICES)

    sender     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sent_helpdesk_messages',
    )
    content    = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        preview = (self.content or '')[:60]
        return f'[{self.role}] {preview}'