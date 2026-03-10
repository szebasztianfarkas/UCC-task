"""
Creates the helpdesk_agent group.
Run once after migrations:
    python manage.py setup_helpdesk
    python manage.py setup_helpdesk --add-agent <username>
    python manage.py setup_helpdesk --remove-agent <username>
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()
GROUP = 'helpdesk_agent'


class Command(BaseCommand):
    help = 'Create the helpdesk_agent group and optionally manage memberships.'

    def add_arguments(self, parser):
        parser.add_argument('--add-agent',    metavar='USERNAME')
        parser.add_argument('--remove-agent', metavar='USERNAME')

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name=GROUP)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Group "{GROUP}" created.'))
        else:
            self.stdout.write(f'Group "{GROUP}" already exists.')

        if username := options.get('add_agent'):
            user = User.objects.get(username=username)
            user.groups.add(group)
            self.stdout.write(self.style.SUCCESS(f'{username} added to {GROUP}.'))

        if username := options.get('remove_agent'):
            user = User.objects.get(username=username)
            user.groups.remove(group)
            self.stdout.write(self.style.SUCCESS(f'{username} removed from {GROUP}.'))