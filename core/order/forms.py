from django import forms
from .models import Order, Address


class CheckoutForm(forms.ModelForm):
    shipping_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        widget=forms.RadioSelect,
        label="آدرس ارسال",
        required=True,
        error_messages={"required": "لطفاً یک آدرس برای ارسال انتخاب کنید"},
    )

    terms_accepted = forms.BooleanField(
        required=True,
        label="شرایط و قوانین را می‌پذیرم",
        error_messages={"required": "برای ثبت سفارش باید شرایط و قوانین را بپذیرید"},
    )

    class Meta:
        model = Order
        fields = ["payment_receipt", "notes"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.fields["shipping_address"].queryset = Address.objects.filter(
            user=user
        ).order_by("-is_default", "-created_date")

        self.fields["shipping_address"].label_from_instance = (
            lambda obj: f"{obj.label} - {obj.get_short_address()}"
        )
