from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from mailings.models import Mailing, MailingAttempt


class Command(BaseCommand):
    help = 'Send scheduled mailings'

    def handle(self, *args, **options):
        now = timezone.now()
        mailings = Mailing.objects.filter(
            status='started', start_time__lte=now, end_time__gte=now
        )

        for mailing in mailings:
            self.send_mailing(mailing)

    def send_mailing(self, mailing):
        try:
            for client in mailing.clients.all():
                success = send_mail(
                    mailing.message.subject,
                    mailing.message.body,
                    'noreply@example.com',
                    [client.email],
                    fail_silently=False,
                )
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='success' if success else 'failed',
                    server_response='OK' if success else 'Failed'
                )
        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing, status='failed', server_response=str(e)
            )