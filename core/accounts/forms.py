from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import (
    PasswordResetForm as DjangoPasswordResetForm,
    SetPasswordForm as DjangoSetPasswordForm,
    PasswordChangeForm as DjangoPasswordChangeForm,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Profile

User = get_user_model()


class UserRegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_("رمز عبور"),
        widget=forms.PasswordInput(
            attrs={"placeholder": "رمز عبور خود را وارد کنید", "class": "form-control"}
        ),
    )
    password2 = forms.CharField(
        label=_("تکرار رمز عبور"),
        widget=forms.PasswordInput(
            attrs={"placeholder": "تکرار رمز عبور", "class": "form-control"}
        ),
    )

    class Meta:
        model = User
        fields = ["email"]
        labels = {
            "email": _("آدرس ایمیل"),
        }
        widgets = {
            "email": forms.EmailInput(
                attrs={"placeholder": "ایمیل خود را وارد کنید", "class": "form-control"}
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("این ایمیل قبلاً ثبت شده است."))
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError(_("رمزهای عبور وارد شده با هم مطابقت ندارند."))
        if len(p1) < 8:
            raise ValidationError(_("رمز عبور باید حداقل ۸ کاراکتر باشد."))
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False  # کاربر تا فعال‌سازی از طریق ایمیل، غیرفعال می‌ماند
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label=_("ایمیل"),
        widget=forms.EmailInput(
            attrs={"placeholder": "ایمیل", "class": "form-control"}
        ),
    )
    password = forms.CharField(
        label=_("رمز عبور"),
        widget=forms.PasswordInput(
            attrs={"placeholder": "رمز عبور", "class": "form-control"}
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise ValidationError(_("ایمیل یا رمز عبور اشتباه است."))
            if not user.is_active:
                raise ValidationError(
                    _("حساب شما هنوز فعال نشده است. لطفاً ایمیل خود را بررسی کنید.")
                )

        return cleaned_data


class CustomPasswordChangeForm(DjangoPasswordChangeForm):
    old_password = forms.CharField(
        label=_("رمز عبور فعلی"),
        widget=forms.PasswordInput(
            attrs={"placeholder": "رمز فعلی", "class": "form-control"}
        ),
    )
    new_password1 = forms.CharField(
        label=_("رمز عبور جدید"),
        widget=forms.PasswordInput(
            attrs={"placeholder": "رمز جدید", "class": "form-control"}
        ),
    )
    new_password2 = forms.CharField(
        label=_("تکرار رمز عبور جدید"),
        widget=forms.PasswordInput(
            attrs={"placeholder": "تکرار رمز جدید", "class": "form-control"}
        ),
    )


class CustomPasswordResetForm(DjangoPasswordResetForm):
    email = forms.EmailField(
        label=_("ایمیل"),
        widget=forms.EmailInput(
            attrs={"placeholder": "ایمیل خود را وارد کنید", "class": "form-control"}
        ),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise ValidationError(_("کاربری با این ایمیل یافت نشد."))
        return email


class CustomSetPasswordForm(DjangoSetPasswordForm):
    new_password1 = forms.CharField(
        label=_("رمز عبور جدید"),
        widget=forms.PasswordInput(
            attrs={"placeholder": "رمز عبور جدید", "class": "form-control"}
        ),
    )
    new_password2 = forms.CharField(
        label=_("تکرار رمز عبور جدید"),
        widget=forms.PasswordInput(
            attrs={"placeholder": "تکرار رمز جدید", "class": "form-control"}
        ),
    )


class ProfileForm(forms.ModelForm):
    """
    Form to create or update a user's profile
    """

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "address", "phone_number", "image"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }
