from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class OwnerRequiredMixin(LoginRequiredMixin):
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='managers').exists()


class OwnerOrManagerMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.groups.filter(name='managers').exists():
            return True
        if hasattr(self, 'get_object'):
            return self.get_object().owner == self.request.user
        return True

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.groups.filter(name='managers').exists():
            return qs
        return qs.filter(owner=self.request.user)