from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Profile


User = get_user_model()


class UserRegisterForm(forms.ModelForm):
    """User registration form with email and password validation."""

    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email"]

    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("این ایمیل قبلاً ثبت شده است."))
        return email

    def clean_password2(self):
        """Validate matching and length of passwords."""
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise ValidationError(_("رمزهای عبور وارد شده با هم مطابقت ندارند."))

        if len(p1) < 8:
            raise ValidationError(_("رمز عبور باید حداقل ۸ کاراکتر باشد."))

        return p2

    def save(self, commit=True):
        """Save the user with an inactive account until verified."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False

        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """User login form using email and password."""

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        """Authenticate user credentials."""
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if not email or not password:
            return cleaned_data

        if not User.objects.filter(email=email).exists():
            raise ValidationError(_("کاربری با این ایمیل یافت نشد."))

        user = authenticate(email=email, password=password)

        if user is None:
            raise ValidationError(_("ایمیل یا رمز عبور اشتباه است."))

        if not user.is_active:
            raise ValidationError(_("حساب شما هنوز فعال نشده است."))

        cleaned_data["user"] = user
        return cleaned_data


class CustomPasswordChangeForm(PasswordChangeForm):
    """Form for changing the user's password."""

    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_new_password2(self):
        """Validate new passwords match and meet requirements."""
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(_("رمزهای عبور وارد شده با هم مطابقت ندارند."))

        if len(password1) < 8:
            raise ValidationError(_("رمز عبور باید حداقل ۸ کاراکتر باشد."))

        return password2

    def clean_old_password(self):
        """Check that the old password is correct."""
        old_password = self.cleaned_data.get("old_password")

        if not self.user.check_password(old_password):
            raise ValidationError(
                _(
                    "رمز عبور قبلی شما اشتباه وارد شده است. "
                    "لطفاً دوباره آن را وارد کنید."
                )
            )
        return old_password


class CustomPasswordResetForm(PasswordResetForm):
    """Form for requesting a password reset link."""

    email = forms.EmailField()

    def clean_email(self):
        """Ensure the email belongs to an existing user."""
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise ValidationError(_("کاربری با این ایمیل یافت نشد."))
        return email


class CustomSetPasswordForm(SetPasswordForm):
    """Form for setting a new password after reset."""

    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_new_password2(self):
        """Validate new passwords match and meet requirements."""
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(_("رمزهای عبور وارد شده با هم مطابقت ندارند."))

        if len(password1) < 8:
            raise ValidationError(_("رمز عبور باید حداقل ۸ کاراکتر باشد."))

        return password2
