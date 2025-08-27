from django import forms
from .models import Client, Message, Mailing
from django.utils import timezone


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']


class MailingForm(forms.ModelForm):
    # Поля для относительного времени (только для создания)
    start_choice = forms.ChoiceField(
        choices=[
            ('now', '🟢 Начать сразу'),
            ('5min', '⏱️ Через 5 минут'),
            ('30min', '⏱️ Через 30 минут'),
            ('1hour', '⏱️ Через 1 час'),
            ('3hours', '⏱️ Через 3 часа'),
            ('tomorrow', '📅 Завтра в это же время'),
            ('custom', '📅 Указать свое время'),
        ],
        label='Когда начать рассылку?',
        initial='now',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    duration_choice = forms.ChoiceField(
        choices=[
            ('1hour', '1 час'),
            ('3hours', '3 часа'),
            ('6hours', '6 часов'),
            ('12hours', '12 часов'),
            ('1day', '1 день'),
            ('3days', '3 дня'),
            ('1week', '1 неделя'),
            ('custom', 'Указать свое время'),
        ],
        label='Как долго работать?',
        initial='1day',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Отдельные поля для кастомного времени
    custom_start = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
        })
    )

    custom_end = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
        })
    )

    class Meta:
        model = Mailing
        fields = ['status', 'message', 'clients']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Select(attrs={'class': 'form-control'}),
            'clients': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['message'].queryset = Message.objects.filter(owner=user)
            self.fields['clients'].queryset = Client.objects.filter(owner=user)

    def clean(self):
        cleaned_data = super().clean()
        start_choice = cleaned_data.get('start_choice')
        duration_choice = cleaned_data.get('duration_choice')
        custom_start = cleaned_data.get('custom_start')
        custom_end = cleaned_data.get('custom_end')

        now = timezone.now()

        # Валидация кастомного времени начала
        if start_choice == 'custom':
            if not custom_start:
                raise forms.ValidationError({'custom_start': 'Укажите дату и время начала'})
            if custom_start < now:
                raise forms.ValidationError({'custom_start': 'Время начала не может быть в прошлом'})
            cleaned_data['start_time'] = custom_start
        else:
            # Устанавливаем время начала из выбора
            if start_choice == 'now':
                cleaned_data['start_time'] = now
            elif start_choice == '5min':
                cleaned_data['start_time'] = now + timezone.timedelta(minutes=5)
            elif start_choice == '30min':
                cleaned_data['start_time'] = now + timezone.timedelta(minutes=30)
            elif start_choice == '1hour':
                cleaned_data['start_time'] = now + timezone.timedelta(hours=1)
            elif start_choice == '3hours':
                cleaned_data['start_time'] = now + timezone.timedelta(hours=3)
            elif start_choice == 'tomorrow':
                cleaned_data['start_time'] = now + timezone.timedelta(days=1)

        # Валидация кастомного времени окончания
        start_time = cleaned_data.get('start_time')
        if not start_time:
            raise forms.ValidationError('Не удалось установить время начала')

        if duration_choice == 'custom':
            if not custom_end:
                raise forms.ValidationError({'custom_end': 'Укажите дату и время окончания'})
            if custom_end <= start_time:
                raise forms.ValidationError({'custom_end': 'Время окончания должно быть позже времени начала'})
            cleaned_data['end_time'] = custom_end
        else:
            # Устанавливаем время окончания из выбора
            if duration_choice == '1hour':
                cleaned_data['end_time'] = start_time + timezone.timedelta(hours=1)
            elif duration_choice == '3hours':
                cleaned_data['end_time'] = start_time + timezone.timedelta(hours=3)
            elif duration_choice == '6hours':
                cleaned_data['end_time'] = start_time + timezone.timedelta(hours=6)
            elif duration_choice == '12hours':
                cleaned_data['end_time'] = start_time + timezone.timedelta(hours=12)
            elif duration_choice == '1day':
                cleaned_data['end_time'] = start_time + timezone.timedelta(days=1)
            elif duration_choice == '3days':
                cleaned_data['end_time'] = start_time + timezone.timedelta(days=3)
            elif duration_choice == '1week':
                cleaned_data['end_time'] = start_time + timezone.timedelta(weeks=1)

        return cleaned_data

    def save(self, commit=True):
        mailing = super().save(commit=False)
        mailing.start_time = self.cleaned_data['start_time']
        mailing.end_time = self.cleaned_data['end_time']

        if commit:
            mailing.save()
            self.save_m2m()

        return mailing
