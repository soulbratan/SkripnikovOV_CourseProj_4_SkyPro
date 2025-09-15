from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailings.models import Mailing, Client, Message


class Command(BaseCommand):
    help = 'Create user groups and assign permissions'

    def handle(self, *args, **options):
        managers_group, created = Group.objects.get_or_create(name='managers')
        if created:
            self.stdout.write(self.style.SUCCESS('Managers group created'))

        models = [Mailing, Client, Message]
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            permissions = Permission.objects.filter(content_type=content_type)
            for perm in permissions:
                if perm.codename.startswith('view_'):
                    managers_group.permissions.add(perm)
