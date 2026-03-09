from django.db import models
from django.conf import settings


class Event(models.Model):
    title       = models.CharField(max_length=255)
    occurrence  = models.DateTimeField()
    description = models.TextField(blank=True, default='')
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_events',
    )
    attendees   = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='attending_events',
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['occurrence']

    def __str__(self):
        return self.title