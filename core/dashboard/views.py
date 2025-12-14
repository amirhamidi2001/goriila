from django.views.generic.base import View, TemplateView
from django.views.generic import DetailView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.db.models import Prefetch, Count

from accounts.models import Profile
from order.models import Order, OrderItem
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


class OrderListView(LoginRequiredMixin, ListView):
    """ """

    model = Order
    template_name = "dashboard/orders.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        """ """
        queryset = (
            Order.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=OrderItem.objects.select_related("product").order_by("id"),
                )
            )
            .annotate(items_count=Count("items"))
            .order_by("-created_date")
        )

        status_filter = self.request.GET.get("status")
        if status_filter and status_filter != "all":
            queryset = queryset.filter(status=status_filter)

        search_query = self.request.GET.get("search")
        if search_query:
            queryset = queryset.filter(order_number__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        """ """
        context = super().get_context_data(**kwargs)

        context["order_stats"] = {
            "all": Order.objects.filter(user=self.request.user).count(),
            "pending": Order.objects.filter(
                user=self.request.user, status="pending"
            ).count(),
            "processing": Order.objects.filter(
                user=self.request.user, status="processing"
            ).count(),
            "shipped": Order.objects.filter(
                user=self.request.user, status="shipped"
            ).count(),
            "delivered": Order.objects.filter(
                user=self.request.user, status="delivered"
            ).count(),
            "cancelled": Order.objects.filter(
                user=self.request.user, status="cancelled"
            ).count(),
        }

        context["current_status"] = self.request.GET.get("status", "all")
        context["search_query"] = self.request.GET.get("search", "")
        context["profile"] = self.request.user.user_profile

        context["status_mapping"] = {
            "pending": {"label": "در انتظار بررسی", "class": "pending"},
            "payment_verified": {"label": "پرداخت تایید شده", "class": "verified"},
            "processing": {"label": "در حال پردازش", "class": "processing"},
            "shipped": {"label": "ارسال شده", "class": "shipped"},
            "delivered": {"label": "تحویل داده شده", "class": "delivered"},
            "cancelled": {"label": "لغو شده", "class": "cancelled"},
        }

        return context


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
                return redirect("dashboard:settings")
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
                return redirect("dashboard:settings")
            else:
                messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.")

        context = {
            "profile": profile,
            "form": personal_info_form,
            "password_form": password_form,
        }

        return render(request, self.template_name, context)


class DashboardWalletView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "dashboard/wallet.html"
    context_object_name = "orders"

    def get_queryset(self):
        queryset = super().get_queryset()
        user_orders = queryset.filter(user=self.request.user)
        return user_orders

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_orders"] = self.get_queryset().count()
        context["orders_with_receipt"] = self.get_queryset().exclude(payment_receipt="")
        context["profile"] = self.request.user.user_profile

        return context


class DashboardWishlistView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "dashboard/wishlist.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """
        Return the profile of the currently logged-in user
        """
        return self.request.user.user_profile
