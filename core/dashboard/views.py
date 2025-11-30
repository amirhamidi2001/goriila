from django.views.generic.base import TemplateView
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from accounts.models import Profile
from .forms import PersonalInformationForm


class DashboardAddressesView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "dashboard/addresses.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """
        Return the profile of the currently logged-in user
        """
        return self.request.user.user_profile


class DashboardOrdersView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "dashboard/orders.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """
        Return the profile of the currently logged-in user
        """
        return self.request.user.user_profile

class DashboardReviewsView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "dashboard/reviews.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """
        Return the profile of the currently logged-in user
        """
        return self.request.user.user_profile


class DashboardSettingsView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = "dashboard/settings.html"
    form_class = PersonalInformationForm
    success_url = reverse_lazy("dashboard:dashboard-settings")

    def get_object(self, queryset=None):
        return self.request.user.user_profile

    def form_valid(self, form):
        messages.success(self.request, "پروفایل با موفقیت به‌روزرسانی شد.")
        return super().form_valid(form)


class DashboardWalletView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "dashboard/wallet.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """
        Return the profile of the currently logged-in user
        """
        return self.request.user.user_profile

class DashboardWishlistView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "dashboard/wishlist.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """
        Return the profile of the currently logged-in user
        """
        return self.request.user.user_profile
