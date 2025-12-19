from django.views.generic.base import View
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.db.models import Prefetch, Count
from django.http import JsonResponse

from shop.models import Wishlist, Product
from accounts.models import Profile
from order.models import Order, OrderItem

from .forms import PersonalInfoForm, ChangePasswordForm


class DashboardAddressesView(LoginRequiredMixin, DetailView):
    """
    Retrieves and displays the profile associated with
    the currently authenticated user.
    """

    model = Profile
    template_name = "dashboard/addresses.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """
        Return the profile of the currently logged-in user.
        """
        return self.request.user.user_profile


class OrderListView(LoginRequiredMixin, ListView):
    """
    Display a paginated list of user orders.
    """

    model = Order
    template_name = "dashboard/orders.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        """
        Return filtered and optimized queryset of user orders.
        """
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
        """
        Add order statistics, filters, and user profile to context.
        """
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
    """
    Shows reviews associated with the current user's profile.
    """

    model = Profile
    template_name = "dashboard/reviews.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """
        Return the profile of the currently logged-in user.
        """
        return self.request.user.user_profile


@method_decorator(login_required, name="dispatch")
class DashboardSettingsView(View):
    """
    Manage user account settings.
    """

    template_name = "dashboard/settings.html"

    def get(self, request):
        """
        Display account settings forms.
        """
        profile, _ = Profile.objects.get_or_create(user=request.user)

        context = {
            "profile": profile,
            "form": PersonalInfoForm(instance=profile),
            "password_form": ChangePasswordForm(request.user),
        }

        return render(request, self.template_name, context)

    def post(self, request):
        """
        Handle form submission for personal info or password change.
        """
        profile, _ = Profile.objects.get_or_create(user=request.user)

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

            messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.")

        context = {
            "profile": profile,
            "form": personal_info_form,
            "password_form": password_form,
        }
        return render(request, self.template_name, context)


class DashboardWalletView(LoginRequiredMixin, ListView):
    """
    Display user wallet and payment-related orders.
    """

    model = Order
    template_name = "dashboard/wallet.html"
    context_object_name = "orders"

    def get_queryset(self):
        """
        Return orders belonging to the current user.
        """
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Add wallet-related statistics to context.
        """
        context = super().get_context_data(**kwargs)
        context["total_orders"] = self.get_queryset().count()
        context["orders_with_receipt"] = self.get_queryset().exclude(payment_receipt="")
        context["profile"] = self.request.user.user_profile
        return context


class DashboardWishlistView(LoginRequiredMixin, ListView):
    """
    Display user's wishlist items.
    """

    model = Wishlist
    template_name = "dashboard/wishlist.html"
    context_object_name = "wishlist_items"
    paginate_by = 12

    def get_queryset(self):
        """
        Return wishlist items with optimized related data.
        """
        return Wishlist.objects.filter(user=self.request.user).select_related(
            "product", "product__brand", "product__category"
        )

    def get_context_data(self, **kwargs):
        """
        Add wishlist statistics to context.
        """
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        context["profile"] = self.request.user.user_profile
        return context


class WishlistDeleteView(LoginRequiredMixin, View):
    """
    Remove an item from the user's wishlist.
    """

    http_method_names = ["post"]

    def post(self, request, pk):
        """
        Delete a wishlist item.
        """
        wishlist_item = get_object_or_404(Wishlist, pk=pk, user=request.user)
        wishlist_item.delete()
        messages.success(request, "محصول از لیست علاقه‌مندی‌ها حذف شد")
        return redirect("dashboard:wishlist")


class WishlistToggleView(LoginRequiredMixin, View):
    """
    Toggle wishlist status for a product (AJAX).
    """

    http_method_names = ["post"]

    def post(self, request):
        """
        Add or remove a product from the wishlist.
        """
        product_id = request.POST.get("product_id")

        if not product_id:
            return JsonResponse({"error": "محصول یافت نشد"}, status=400)

        product = get_object_or_404(Product, id=product_id)

        wishlist_item = Wishlist.objects.filter(
            user=request.user, product=product
        ).first()

        if wishlist_item:
            wishlist_item.delete()
            added = False
            message = "محصول از لیست علاقه‌مندی‌ها حذف شد"
        else:
            Wishlist.objects.create(user=request.user, product=product)
            added = True
            message = "محصول به لیست علاقه‌مندی‌ها اضافه شد"

        total_items = Wishlist.objects.filter(user=request.user).count()

        return JsonResponse(
            {
                "added": added,
                "message": message,
                "total_wishlist_items": total_items,
            }
        )
