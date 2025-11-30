from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    PasswordChangeForm,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from accounts.models import Profile
from accounts.validators import validate_iranian_cellphone_number


class PersonalInformationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "phone_number"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "phone_number": "شماره تلفن",
        }

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


# class AddressForm(forms.Form):
#     address_type = forms.CharField(
#         max_length=50,
#         required=True,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'e.g., Home, Office'
#         })
#     )
#     full_name = forms.CharField(
#         max_length=200,
#         required=True,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control'
#         })
#     )
#     phone = forms.CharField(
#         max_length=17,
#         required=True,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control'
#         })
#     )
#     address_line1 = forms.CharField(
#         max_length=255,
#         required=True,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Street address'
#         })
#     )
#     address_line2 = forms.CharField(
#         max_length=255,
#         required=False,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Apartment, suite, etc. (optional)'
#         })
#     )
#     city = forms.CharField(
#         max_length=100,
#         required=True,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control'
#         })
#     )
#     state = forms.CharField(
#         max_length=100,
#         required=True,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control'
#         })
#     )
#     postal_code = forms.CharField(
#         max_length=20,
#         required=True,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control'
#         })
#     )
#     country = forms.CharField(
#         max_length=100,
#         required=True,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control'
#         })
#     )
#     is_default = forms.BooleanField(
#         required=False,
#         widget=forms.CheckboxInput(attrs={
#             'class': 'form-check-input'
#         })
#     )


# class PaymentMethodForm(forms.Form):
#     CARD_TYPES = [
#         ('visa', 'Visa'),
#         ('mastercard', 'Mastercard'),
#         ('amex', 'American Express'),
#         ('discover', 'Discover'),
#     ]
    
#     card_type = forms.ChoiceField(
#         choices=CARD_TYPES,
#         required=True,
#         widget=forms.Select(attrs={
#             'class': 'form-control'
#         })
#     )
#     card_number = forms.CharField(
#         max_length=19,
#         required=True,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': '•••• •••• •••• ••••'
#         })
#     )
#     expiry_date = forms.CharField(
#         max_length=7,
#         required=True,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'MM/YYYY'
#         })
#     )
#     is_default = forms.BooleanField(
#         required=False,
#         widget=forms.CheckboxInput(attrs={
#             'class': 'form-check-input'
#         })
#     )


# class EmailPreferencesForm(forms.Form):
#     order_updates = forms.BooleanField(
#         required=False,
#         widget=forms.CheckboxInput(attrs={
#             'class': 'form-check-input',
#             'id': 'orderUpdates'
#         })
#     )
#     promotions = forms.BooleanField(
#         required=False,
#         widget=forms.CheckboxInput(attrs={
#             'class': 'form-check-input',
#             'id': 'promotions'
#         })
#     )
#     newsletter = forms.BooleanField(
#         required=False,
#         widget=forms.CheckboxInput(attrs={
#             'class': 'form-check-input',
#             'id': 'newsletter'
#         })
#     )