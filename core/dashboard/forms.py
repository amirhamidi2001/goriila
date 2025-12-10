from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

from accounts.models import Profile
from order.models import Address


class PersonalInfoForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "phone_number", "image"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام خانوادگی"}
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "09123456789 - اعداد با انگلیسی وارد شوند",
                }
            ),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }
        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "phone_number": "شماره موبایل",
            "image": "تصویر پروفایل",
        }


class ChangePasswordForm(forms.Form):

    current_password = forms.CharField(
        label="رمز عبور فعلی",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "رمز عبور فعلی"}
        ),
    )
    new_password = forms.CharField(
        label="رمز عبور جدید",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "رمز عبور جدید"}
        ),
        validators=[validate_password],
    )
    confirm_password = forms.CharField(
        label="تأیید رمز عبور",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "تأیید رمز عبور"}
        ),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get("current_password")
        if not self.user.check_password(current_password):
            raise ValidationError("رمز عبور فعلی صحیح نیست.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("رمز عبور جدید و تأیید رمز عبور مطابقت ندارند.")

        return cleaned_data


class AddressForm(forms.ModelForm):
    """Form for creating and updating addresses"""

    class Meta:
        model = Address
        fields = [
            "label",
            "address_type",
            "full_name",
            "phone",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "postal_code",
            "country",
            "is_default",
        ]
        widgets = {
            "label": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "مثال: خانه، محل کار، خانه والدین",
                }
            ),
            "address_type": forms.Select(attrs={"class": "form-select"}),
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام کامل"}
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "09123456789 - اعداد با انگلیسی وارد شوند",
                }
            ),
            "address_line1": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "آدرس خیابان"}
            ),
            "address_line2": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "آپارتمان، واحد، طبقه و ... (اختیاری)",
                }
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "شهر"}
            ),
            "state": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "استان"}
            ),
            "postal_code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "کد پستی"}
            ),
            "country": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "کشور"}
            ),
            "is_default": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Make some fields required
        self.fields["label"].required = True
        self.fields["full_name"].required = True
        self.fields["phone"].required = True
        self.fields["address_line1"].required = True
        self.fields["city"].required = True
        self.fields["state"].required = True
        self.fields["postal_code"].required = True

    def clean(self):
        cleaned_data = super().clean()
        is_default = cleaned_data.get("is_default")

        # If this is the only address for the user, it must be default
        if self.user and not self.instance.pk:
            if not Address.objects.filter(user=self.user).exists():
                cleaned_data["is_default"] = True

        return cleaned_data


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
