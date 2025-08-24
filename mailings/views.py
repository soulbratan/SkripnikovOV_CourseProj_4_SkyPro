from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Q
from django.core.cache import cache
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone

from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm
from .mixins import OwnerRequiredMixin, ManagerRequiredMixin, OwnerOrManagerMixin


class IndexView(TemplateView):
    """Главная страница с общей статистикой"""
    template_name = 'mailings/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Кеширование статистики на 5 минут
        cache_key = 'mailing_stats'
        stats = cache.get(cache_key)

        if not stats:
            stats = {
                'total_mailings': Mailing.objects.count(),
                'active_mailings': Mailing.objects.filter(status='started').count(),
                'unique_clients': Client.objects.count(),
            }
            cache.set(cache_key, stats, 300)  # 5 минут

        context.update(stats)
        return context


# Client Views
class ClientListView(OwnerOrManagerMixin, ListView):
    """Список клиентов"""
    model = Client
    template_name = 'mailings/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10


class ClientCreateView(LoginRequiredMixin, CreateView):
    """Создание клиента"""
    model = Client
    form_class = ClientForm
    template_name = 'mailings/client_form.html'
    success_url = reverse_lazy('mailings:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Клиент успешно создан!')
        return super().form_valid(form)


class ClientUpdateView(OwnerRequiredMixin, UpdateView):
    """Редактирование клиента"""
    model = Client
    form_class = ClientForm
    template_name = 'mailings/client_form.html'
    success_url = reverse_lazy('mailings:client_list')

    def form_valid(self, form):
        messages.success(self.request, 'Клиент успешно обновлен!')
        return super().form_valid(form)


class ClientDeleteView(OwnerRequiredMixin, DeleteView):
    """Удаление клиента"""
    model = Client
    template_name = 'mailings/client_confirm_delete.html'
    success_url = reverse_lazy('mailings:client_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Клиент успешно удален!')
        return super().delete(request, *args, **kwargs)


# Message Views
class MessageListView(OwnerOrManagerMixin, ListView):
    """Список сообщений"""
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'
    paginate_by = 10


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Создание сообщения"""
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Сообщение успешно создано!')
        return super().form_valid(form)


class MessageUpdateView(OwnerRequiredMixin, UpdateView):
    """Редактирование сообщения"""
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение успешно обновлено!')
        return super().form_valid(form)


class MessageDeleteView(OwnerRequiredMixin, DeleteView):
    """Удаление сообщения"""
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Сообщение успешно удалено!')
        return super().delete(request, *args, **kwargs)


# Mailing Views
class MailingListView(OwnerOrManagerMixin, ListView):
    """Список рассылок"""
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'
    paginate_by = 10


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Создание рассылки"""
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Рассылка успешно создана!')
        return super().form_valid(form)


class MailingUpdateView(OwnerRequiredMixin, UpdateView):
    """Редактирование рассылки"""
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка успешно обновлена!')
        return super().form_valid(form)


class MailingDeleteView(OwnerRequiredMixin, DeleteView):
    """Удаление рассылки"""
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Рассылка успешно удалена!')
        return super().delete(request, *args, **kwargs)


class MailingDetailView(OwnerOrManagerMixin, DetailView):
    """Детальный просмотр рассылки"""
    model = Mailing
    template_name = 'mailings/mailing_detail.html'
    context_object_name = 'mailing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attempts'] = MailingAttempt.objects.filter(
            mailing=self.object
        ).order_by('-attempt_time')[:10]
        return context


class MailingAttemptListView(LoginRequiredMixin, ListView):
    """Список попыток рассылок"""
    model = MailingAttempt
    template_name = 'mailings/attempt_list.html'
    context_object_name = 'attempts'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm('mailings.view_mailingattempt'):
            return qs.select_related('mailing', 'mailing__message')
        return qs.filter(mailing__owner=self.request.user).select_related('mailing', 'mailing__message')


class StatisticsView(LoginRequiredMixin, TemplateView):
    """Страница статистики"""
    template_name = 'mailings/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Статистика по рассылкам пользователя
        user_mailings = Mailing.objects.filter(owner=self.request.user)

        mailing_stats = user_mailings.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(status='started')),
            completed=Count('id', filter=Q(status='completed')),
            created=Count('id', filter=Q(status='created')),
            disabled=Count('id', filter=Q(status='disabled'))
        )

        # Статистика по попыткам
        attempts = MailingAttempt.objects.filter(mailing__owner=self.request.user)
        attempt_stats = attempts.aggregate(
            total=Count('id'),
            success=Count('id', filter=Q(status='success')),
            failed=Count('id', filter=Q(status='failed'))
        )

        # Топ рассылок
        top_mailings = user_mailings.annotate(
            attempt_count=Count('mailingattempt'),
            success_attempts=Count('mailingattempt', filter=Q(mailingattempt__status='success'))
        ).order_by('-attempt_count')[:5]

        context['mailing_stats'] = mailing_stats
        context['attempt_stats'] = attempt_stats
        context['top_mailings'] = top_mailings

        return context


# Manager Views
class ManagerDashboardView(ManagerRequiredMixin, TemplateView):
    """Панель управления для менеджеров"""
    template_name = 'mailings/manager_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from django.contrib.auth import get_user_model
        User = get_user_model()

        context['total_users'] = User.objects.count()
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='started').count()
        context['recent_mailings'] = Mailing.objects.select_related(
            'owner', 'message'
        ).order_by('-id')[:10]

        return context


# Function-based views
@login_required
def send_mailing_now(request, pk):
    """Ручная отправка рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверка прав доступа
    if mailing.owner != request.user and not request.user.has_perm('mailings.disable_mailing'):
        messages.error(request, 'У вас нет прав для отправки этой рассылки!')
        return redirect('mailings:mailing_list')

    try:
        # Отправка рассылки
        success_count = 0
        total_count = mailing.clients.count()

        for client in mailing.clients.all():
            try:
                send_mail(
                    mailing.message.subject,
                    mailing.message.body,
                    'pochtoviyserversov@yandex.ru',
                    [client.email],
                    fail_silently=False,
                )
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='success',
                    server_response='Успешно отправлено'
                )
                success_count += 1
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='failed',
                    server_response=str(e)
                )

        messages.success(
            request,
            f'Рассылка отправлена! Успешно: {success_count}/{total_count}'
        )

    except Exception as e:
        messages.error(request, f'Ошибка при отправке рассылки: {str(e)}')

    return redirect('mailings:mailing_detail', pk=pk)


@login_required
@permission_required('mailings.disable_mailing', raise_exception=True)
def toggle_mailing_status(request, pk):
    """Переключение статуса рассылки (для менеджеров)"""
    mailing = get_object_or_404(Mailing, pk=pk)

    if mailing.status == 'started':
        mailing.status = 'disabled'
        mailing.save()
        messages.success(request, 'Рассылка отключена!')
    elif mailing.status == 'disabled':
        mailing.status = 'started'
        mailing.save()
        messages.success(request, 'Рассылка включена!')
    else:
        messages.warning(request, 'Невозможно изменить статус этой рассылки!')

    return redirect('mailings:mailing_list')


@login_required
def mailing_stats_json(request, pk):
    """JSON API для статистики рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk)

    if mailing.owner != request.user and not request.user.has_perm('mailings.view_mailing'):
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)

    attempts = MailingAttempt.objects.filter(mailing=mailing)
    stats = attempts.aggregate(
        total=Count('id'),
        success=Count('id', filter=Q(status='success')),
        failed=Count('id', filter=Q(status='failed'))
    )

    return JsonResponse({
        'mailing_id': mailing.id,
        'status': mailing.get_status_display(),
        'attempts': stats,
        'success_rate': round((stats['success'] / stats['total'] * 100), 2) if stats['total'] > 0 else 0
    })