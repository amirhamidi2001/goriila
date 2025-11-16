from django.views.generic.base import TemplateView
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Profile


class DashboardView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "dashboard/account.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """
        Return the profile of the currently logged-in user
        """
        return self.request.user.user_profile
