from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bio    = models.TextField(blank=True, default='')

    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='evently_users',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='evently_users',
        verbose_name='user permissions',
    )

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=['is_active'])