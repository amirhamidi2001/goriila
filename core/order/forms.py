from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    """Form for checkout process"""
    
    shipping_address = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='آدرس ارسال',
        error_messages={
            'required': 'لطفاً یک آدرس برای ارسال انتخاب کنید.'
        }
    )
    
    payment_receipt = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'receipt'
        }),
        label='فیش کارت‌به‌کارت',
        error_messages={
            'required': 'لطفاً فیش واریز را بارگذاری کنید.'
        }
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'terms'
        }),
        label='موافقت با شرایط و ضوابط',
        error_messages={
            'required': 'برای ثبت سفارش باید شرایط و ضوابط را بپذیرید.'
        }
    )
    
    class Meta:
        model = Order
        fields = ['shipping_address', 'payment_receipt', 'terms_accepted']
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get user's addresses
        from .models import Address
        addresses = Address.objects.filter(user=user).order_by('-is_default', '-created_date')
        
        # Create choices for addresses
        address_choices = [
            (str(addr.id), f"{addr.state}، {addr.city}، {addr.address_line1}")
            for addr in addresses
        ]
        
        if not address_choices:
            address_choices = [('', 'هیچ آدرسی ثبت نشده است')]
        
        self.fields['shipping_address'].choices = address_choices
        
        # Set default address if exists
        default_address = addresses.filter(is_default=True).first()
        if default_address:
            self.fields['shipping_address'].initial = str(default_address.id)
    
    def clean_payment_receipt(self):
        receipt = self.cleaned_data.get('payment_receipt')
        
        if receipt:
            # Validate file size (max 5MB)
            if receipt.size > 5 * 1024 * 1024:
                raise forms.ValidationError('حجم فایل نباید بیشتر از 5 مگابایت باشد.')
            
            # Validate file type
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            ext = receipt.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError('فقط فایل‌های تصویری مجاز هستند.')
        
        return receipt
    
    def clean_shipping_address(self):
        address_id = self.cleaned_data.get('shipping_address')
        
        if not address_id or address_id == '':
            raise forms.ValidationError('لطفاً یک آدرس برای ارسال انتخاب کنید.')
        
        return address_id