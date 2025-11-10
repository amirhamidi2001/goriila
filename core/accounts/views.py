from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model,
    update_session_auth_hash,
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import View, FormView, TemplateView
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMultiAlternatives
from .models import Profile
from .forms import ProfileForm
from .forms import (
    UserRegisterForm,
    UserLoginForm,
    CustomPasswordChangeForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
)

User = get_user_model()


def send_activation_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    current_site = get_current_site(request)
    domain = current_site.domain
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
    template_name = "accounts/register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        user = form.save()
        send_activation_email(self.request, user)
        messages.success(
            self.request,
            "ثبت‌نام شما با موفقیت انجام شد. ایمیل فعال‌سازی برای شما ارسال شد. لطفاً ایمیل خود را بررسی کنید.",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "لطفاً خطاهای فرم را بررسی کنید.")
        return super().form_invalid(form)


class ActivateView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_verified = True
            user.save()
            messages.success(
                request, "حساب کاربری شما با موفقیت فعال شد. اکنون می‌توانید وارد شوید."
            )
            return redirect("accounts:login")
        else:
            messages.error(request, "لینک فعال‌سازی نامعتبر است یا منقضی شده است.")
            return redirect("accounts:register")


class LoginView(FormView):
    template_name = "accounts/login.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("website:index")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "شما هم‌اکنون وارد شده‌اید.")
            return redirect("website:index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        user = authenticate(self.request, email=email, password=password)

        if user:
            if not user.is_active:
                form.add_error(
                    None, "حساب شما هنوز فعال نشده است. لطفاً ایمیل خود را بررسی کنید."
                )
                return self.form_invalid(form)

            login(self.request, user)
            messages.success(self.request, "ورود با موفقیت انجام شد.")
            return super().form_valid(form)
        else:
            form.add_error(None, "ایمیل یا رمز عبور اشتباه است.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "فرم ورود نامعتبر است.")
        return super().form_invalid(form)


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, "شما با موفقیت خارج شدید.")
        return redirect("accounts:login")


class PasswordChangeView(LoginRequiredMixin, FormView):
    template_name = "accounts/password_change.html"
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy("website:index")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, "رمز عبور شما با موفقیت تغییر یافت.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "لطفاً خطاهای فرم را بررسی کنید.")
        return super().form_invalid(form)


class PasswordResetView(FormView):
    template_name = "accounts/password_reset.html"
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
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

        text_content = f"برای فعال‌سازی حساب خود روی لینک زیر کلیک کنید:\n{reset_link}"

        email = EmailMultiAlternatives(subject, text_content, from_email, to)
        email.attach_alternative(html_content, "text/html")
        email.send()

        messages.success(self.request, "لینک بازیابی رمز عبور به ایمیل شما ارسال شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "فرم نامعتبر است.")
        return super().form_invalid(form)


class PasswordResetConfirmView(FormView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            self.user = None

        if self.user is None or not default_token_generator.check_token(
            self.user, token
        ):
            messages.error(request, "لینک بازیابی رمز عبور نامعتبر یا منقضی شده است.")
            return redirect("accounts:password_reset")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "رمز عبور شما با موفقیت بازنشانی شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "فرم نامعتبر است.")
        return super().form_invalid(form)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """
    Displays a user's profile
    """

    model = Profile
    template_name = "accounts/profile_detail.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """
        Return the profile of the currently logged-in user
        """
        return self.request.user.user_profile


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Allows a user to update their profile
    """

    model = Profile
    form_class = ProfileForm
    template_name = "accounts/profile_update.html"
    success_url = reverse_lazy("accounts:profile_detail")

    def get_object(self, queryset=None):
        """
        Return the profile of the currently logged-in user
        """
        return self.request.user.user_profile
