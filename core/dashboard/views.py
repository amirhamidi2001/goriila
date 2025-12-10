from django.views.generic.base import TemplateView
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import update_session_auth_hash

from accounts.models import Profile
from .forms import PersonalInfoForm, ChangePasswordForm


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


@method_decorator(login_required, name="dispatch")
class DashboardSettingsView(View):

    template_name = "dashboard/settings.html"

    def get(self, request):
        try:
            profile = request.user.user_profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)

        personal_info_form = PersonalInfoForm(instance=profile)
        password_form = ChangePasswordForm(request.user)

        context = {
            "profile": profile,
            "form": personal_info_form,
            "password_form": password_form,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        try:
            profile = request.user.user_profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)

        if "current_password" in request.POST:
            password_form = ChangePasswordForm(request.user, request.POST)
            personal_info_form = PersonalInfoForm(instance=profile)

            if password_form.is_valid():
                new_password = password_form.cleaned_data["new_password"]
                request.user.set_password(new_password)
                request.user.save()

                update_session_auth_hash(request, request.user)

                messages.success(request, "رمز عبور شما با موفقیت تغییر یافت.")
                return redirect("dashboard:dashboard-settings")
            else:
                messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.")

        else:
            personal_info_form = PersonalInfoForm(
                request.POST, request.FILES, instance=profile
            )
            password_form = ChangePasswordForm(request.user)

            if personal_info_form.is_valid():
                personal_info_form.save()

                messages.success(request, "اطلاعات شخصی شما با موفقیت به‌روزرسانی شد.")
                return redirect("dashboard:dashboard-settings")
            else:
                messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.")

        context = {
            "profile": profile,
            "form": personal_info_form,
            "password_form": password_form,
        }

        return render(request, self.template_name, context)


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
