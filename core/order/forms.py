from django import forms
from .models import Order, Address


class CheckoutForm(forms.ModelForm):
    """Form for checkout process"""
    
    shipping_address = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        empty_label="آدرس خود را انتخاب کنید",
        widget=forms.RadioSelect,
        label='آدرس ارسال',
        required=True,
        help_text='یکی از آدرس‌های ذخیره شده خود را انتخاب کنید'
    )
    
    payment_receipt = forms.ImageField(
        label='رسید پرداخت',
        help_text='تصویر رسید واریز خود را آپلود کنید',
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    notes = forms.CharField(
        label='یادداشت (اختیاری)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'توضیحات اضافی در مورد سفارش خود...'
        })
    )
    
    terms_accepted = forms.BooleanField(
        label='شرایط و قوانین را می‌پذیرم',
        required=True,
        error_messages={
            'required': 'برای ثبت سفارش باید شرایط و قوانین را بپذیرید'
        }
    )
    
    class Meta:
        model = Order
        fields = ['payment_receipt', 'notes']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Set queryset for shipping address
            self.fields['shipping_address'].queryset = Address.objects.filter(
                user=user
            ).order_by('-is_default', '-created_date')
            
            # Customize the radio button labels to show full address
            self.fields['shipping_address'].label_from_instance = (
                lambda obj: f"{obj.label} - {obj.get_short_address()}"
            )
    
    def clean(self):
        cleaned_data = super().clean()
        shipping_address = cleaned_data.get('shipping_address')
        
        if not shipping_address:
            raise forms.ValidationError(
                'لطفاً یک آدرس برای ارسال انتخاب کنید'
            )
        
        return cleaned_data
    