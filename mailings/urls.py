from django.urls import path
from . import views

app_name = 'mailings'

urlpatterns = [
    # Главная страница
    path('', views.IndexView.as_view(), name='index'),

    # Статистика и отчеты
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),

    # Попытки рассылок
    path('attempts/', views.MailingAttemptListView.as_view(), name='attempt_list'),

    # API endpoints
    path('api/mailing/<int:pk>/stats/', views.mailing_stats_json, name='mailing_stats_json'),

    # Клиенты - CRUD
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),

    # Сообщения - CRUD
    path('messages/', views.MessageListView.as_view(), name='message_list'),
    path('messages/create/', views.MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/edit/', views.MessageUpdateView.as_view(), name='message_edit'),
    path('messages/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),

    # Рассылки - CRUD
    path('mailings/', views.MailingListView.as_view(), name='mailing_list'),
    path('mailings/create/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/edit/', views.MailingUpdateView.as_view(), name='mailing_edit'),
    path('mailings/<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailings/<int:pk>/', views.MailingDetailView.as_view(), name='mailing_detail'),

    # Действия с рассылками
    path('mailings/<int:pk>/send/', views.send_mailing_now, name='send_mailing'),
    path('mailings/<int:pk>/toggle/', views.toggle_mailing_status, name='toggle_mailing'),

    # Панель управления менеджера
    path('manager/dashboard/', views.ManagerDashboardView.as_view(), name='manager_dashboard'),
]