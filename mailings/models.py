from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Client(models.Model):
    email = models.EmailField(_('Email'), unique=True)
    full_name = models.CharField(_('Full name'), max_length=255)
    comment = models.TextField(_('Comment'), blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Message(models.Model):
    subject = models.CharField(_('Subject'), max_length=255)
    body = models.TextField(_('Body'))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', _('Created')),
        ('started', _('Started')),
        ('completed', _('Completed')),
        ('disabled', _('Disabled')),
    ]

    start_time = models.DateTimeField(_('Start time'))
    end_time = models.DateTimeField(_('End time'))
    status = models.CharField(_('Status'), max_length=10, choices=STATUS_CHOICES, default='created')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ('success', _('Success')),
        ('failed', _('Failed')),
    ]

    attempt_time = models.DateTimeField(_('Attempt time'), auto_now_add=True)
    status = models.CharField(_('Status'), max_length=7, choices=STATUS_CHOICES)
    server_response = models.TextField(_('Server response'), blank=True)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
