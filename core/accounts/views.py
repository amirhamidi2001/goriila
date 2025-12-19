from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import FormView, View

from .forms import (
    CustomPasswordChangeForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    UserLoginForm,
    UserRegisterForm,
)

User = get_user_model()


def send_activation_email(request, user):
    """
    Send an account activation email to the newly registered user.
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = get_current_site(request).domain
    activation_link = f"http://{domain}/accounts/activate/{uid}/{token}/"

    subject = "فعال‌سازی حساب کاربری شما"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    html_content = render_to_string(
        "accounts/email_activation.html",
        {"user": user, "activation_link": activation_link},
    )
    text_content = f"برای فعال‌سازی حساب خود روی لینک زیر کلیک کنید:\n{activation_link}"

    email = EmailMultiAlternatives(subject, text_content, from_email, to)
    email.attach_alternative(html_content, "text/html")
    email.send()


class RegisterView(FormView):
    """
    Handle user registration.
    """

    template_name = "accounts/register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        """
        Save the user and send activation email if the form is valid.
        """
        user = form.save()
        send_activation_email(self.request, user)
        messages.success(
            self.request,
            "ثبت‌نام شما با موفقیت انجام شد. ایمیل فعال‌سازی برای شما ارسال شد.",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Handle invalid registration form submission.
        """
        messages.error(self.request, "لطفاً خطاهای فرم را بررسی کنید.")
        return super().form_invalid(form)


class ActivateView(View):
    """
    Activate a user account using a UID and token.
    """

    def get(self, request, uidb64, token):
        """
        Validate activation token and activate the user.
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_verified = True
            user.save()
            messages.success(request, "حساب کاربری شما با موفقیت فعال شد.")
            return redirect("accounts:login")

        messages.error(request, "لینک فعال‌سازی نامعتبر یا منقضی شده است.")
        return redirect("accounts:register")


class LoginView(FormView):
    """
    Prevents already authenticated users from accessing the login page.
    """

    template_name = "accounts/login.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("website:index")

    def dispatch(self, request, *args, **kwargs):
        """
        Redirect authenticated users away from the login page.
        """
        if request.user.is_authenticated:
            messages.info(request, "شما هم‌اکنون وارد شده‌اید.")
            return redirect("website:index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Log the user in if credentials are valid.
        """
        user = form.cleaned_data.get("user")
        if user is None:
            messages.error(self.request, "ورود ناموفق بود.")
            return self.form_invalid(form)

        login(self.request, user)
        messages.success(self.request, "ورود با موفقیت انجام شد.")
        return super().form_valid(form)


class LogoutView(LoginRequiredMixin, View):
    """
    Log out the currently authenticated user.
    """

    def get(self, request):
        """
        Perform logout and redirect to login page.
        """
        logout(request)
        messages.success(request, "شما با موفقیت خارج شدید.")
        return redirect("accounts:login")


class PasswordChangeView(LoginRequiredMixin, FormView):
    """
    Allow logged-in users to change their password.
    """

    template_name = "accounts/password_change.html"
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy("website:index")

    def get_form_kwargs(self):
        """
        Pass the current user to the password change form.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Save new password and update session authentication hash.
        """
        user = form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, "رمز عبور با موفقیت تغییر یافت.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Handle invalid password change form.
        """
        messages.error(self.request, "لطفاً خطاهای فرم را بررسی کنید.")
        return super().form_invalid(form)


class PasswordResetView(FormView):
    """
    Handle password reset requests via email.
    """

    template_name = "accounts/password_reset.html"
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        """
        Send password reset email if user exists.
        """
        user_email = form.cleaned_data["email"]
        user = User.objects.get(email=user_email)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(self.request).domain
        reset_link = f"http://{domain}/accounts/reset/{uid}/{token}/"

        subject = "بازیابی رمز عبور"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user.email]

        html_content = render_to_string(
            "accounts/password_reset_email.html",
            {"user": user, "reset_link": reset_link},
        )

        email = EmailMultiAlternatives(subject, reset_link, from_email, to)
        email.attach_alternative(html_content, "text/html")
        email.send()

        messages.success(self.request, "لینک بازیابی رمز عبور ارسال شد.")
        return super().form_valid(form)


class PasswordResetConfirmView(FormView):
    """
    Confirm password reset using UID and token.
    """

    template_name = "accounts/password_reset_confirm.html"
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, uidb64, token, *args, **kwargs):
        """
        Validate reset token before displaying the form.
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            self.user = None

        if self.user is None or not default_token_generator.check_token(
            self.user, token
        ):
            messages.error(request, "لینک نامعتبر یا منقضی شده است.")
            return redirect("accounts:password_reset")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        Pass the user instance to the set password form.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def form_valid(self, form):
        """
        Save the new password.
        """
        form.save()
        messages.success(
            self.request,
            "رمز عبور با موفقیت تغییر یافت. اکنون می‌توانید وارد شوید.",
        )
        return super().form_valid(form)
