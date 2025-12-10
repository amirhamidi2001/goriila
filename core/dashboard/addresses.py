from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.http import JsonResponse
from order.models import Address
from .forms import AddressForm


class AddressListView(LoginRequiredMixin, ListView):
    """Display all addresses for the logged-in user"""

    model = Address
    template_name = "dashboard/addresses.html"
    context_object_name = "addresses"

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.request.user.user_profile
        return context


class AddressCreateView(LoginRequiredMixin, CreateView):
    """Create a new address"""

    model = Address
    form_class = AddressForm
    template_name = "dashboard/address_form.html"
    success_url = reverse_lazy("dashboard:addresses")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "آدرس با موفقیت اضافه شد!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "لطفا خطاهای زیر را اصلاح کنید.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.request.user.user_profile
        return context


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing address"""

    model = Address
    form_class = AddressForm
    template_name = "dashboard/address_form.html"
    success_url = reverse_lazy("dashboard:addresses")

    def get_queryset(self):
        # Ensure users can only edit their own addresses
        return Address.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "آدرس با موفقیت به‌روزرسانی شد!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "لطفا خطاهای زیر را اصلاح کنید.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.request.user.user_profile
        return context


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    """Delete an address"""

    model = Address
    success_url = reverse_lazy("dashboard:addresses")

    def get_queryset(self):
        # Ensure users can only delete their own addresses
        return Address.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Don't allow deletion if it's the only address
        if Address.objects.filter(user=request.user).count() == 1:
            messages.error(request, "شما باید حداقل یک آدرس داشته باشید.")
            return redirect("dashboard:addresses")

        # If deleting default address, make another address default
        if self.object.is_default:
            other_address = (
                Address.objects.filter(user=request.user)
                .exclude(pk=self.object.pk)
                .first()
            )
            if other_address:
                other_address.is_default = True
                other_address.save()

        messages.success(request, "آدرس با موفقیت حذف شد!")
        return super().delete(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Allow GET request for deletion (will be called via AJAX)
        return self.delete(request, *args, **kwargs)


class AddressSetDefaultView(LoginRequiredMixin, View):
    """Set an address as default"""

    def post(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)

        # Remove default flag from all other addresses
        Address.objects.filter(user=request.user).update(is_default=False)

        # Set this address as default
        address.is_default = True
        address.save()

        messages.success(request, f"{address.label} به عنوان آدرس پیش‌فرض تنظیم شد!")

        # Return JSON response for AJAX requests
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": True, "message": "آدرس پیش‌فرض با موفقیت به‌روزرسانی شد!"}
            )

        return redirect("dashboard:addresses")

    def get(self, request, pk):
        # Allow GET request as well
        return self.post(request, pk)
