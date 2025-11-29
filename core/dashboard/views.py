from django.views.generic.base import TemplateView
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Profile

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


class DashboardSettingsView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "dashboard/settings.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """
        Return the profile of the currently logged-in user
        """
        return self.request.user.user_profile



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
