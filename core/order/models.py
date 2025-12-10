from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal
from accounts.validators import validate_iranian_cellphone_number
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Address(models.Model):
    """Model for storing user addresses"""

    ADDRESS_TYPE_CHOICES = (
        ("home", "خانه"),
        ("office", "محل کار"),
        ("other", "سایر"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="addresses", verbose_name="User"
    )

    # Address type and label
    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPE_CHOICES,
        default="home",
        verbose_name="Address Type",
    )
    label = models.CharField(
        max_length=100,
        verbose_name="Label",
    )

    # Contact information
    full_name = models.CharField(max_length=200, verbose_name="Full Name")
    phone = models.CharField(
        max_length=12,
        validators=[validate_iranian_cellphone_number],
        verbose_name="Phone Number",
    )

    # Address fields
    address_line1 = models.CharField(max_length=255, verbose_name="Address Line 1")
    address_line2 = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Address Line 2 (Optional)"
    )
    city = models.CharField(max_length=100, verbose_name="City")
    state = models.CharField(max_length=100, verbose_name="State/Province")
    postal_code = models.CharField(max_length=20, verbose_name="Postal Code")
    country = models.CharField(max_length=100, default="ایران", verbose_name="Country")

    # Default address flag
    is_default = models.BooleanField(default=False, verbose_name="Default Address")

    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ["-is_default", "-created_date"]

    def __str__(self):
        return f"{self.label} - {self.city}, {self.state}"

    def save(self, *args, **kwargs):
        # If this address is set as default, remove default flag from other addresses
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(
                pk=self.pk
            ).update(is_default=False)

        # If this is the first address for the user, make it default
        if not self.pk and not Address.objects.filter(user=self.user).exists():
            self.is_default = True

        super().save(*args, **kwargs)

    def get_full_address(self):
        """Return formatted full address"""
        address_parts = [
            self.address_line1,
            self.address_line2,
            f"{self.city}, {self.state} {self.postal_code}",
            self.country,
        ]
        return "<br />".join(filter(None, address_parts))

    def get_short_address(self):
        """Return short version of address"""
        return f"{self.address_line1}, {self.city}, {self.state}"



class Order(models.Model):
    """Model for storing orders"""
    
    STATUS_CHOICES = (
        ('pending', 'در انتظار بررسی'),
        ('confirmed', 'تایید شده'),
        ('processing', 'در حال پردازش'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'در انتظار تایید'),
        ('confirmed', 'تایید شده'),
        ('rejected', 'رد شده'),
    )
    
    # User and tracking
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    order_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False
    )
    
    # Shipping address
    shipping_address = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    
    # Payment receipt
    payment_receipt = models.ImageField(
        upload_to='payment_receipts/%Y/%m/%d/',
        null=True,
        blank=True
    )
    
    # Order details
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)]
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    # Terms acceptance
    terms_accepted = models.BooleanField(default=False)
    
    # Notes
    admin_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.user.email}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            import uuid
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_id = str(uuid.uuid4())[:8].upper()
            self.order_number = f"ORD-{timestamp}-{unique_id}"
        super().save(*args, **kwargs)
    
    def get_status_display_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'pending': 'warning',
            'confirmed': 'info',
            'processing': 'primary',
            'shipped': 'secondary',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        return status_classes.get(self.status, 'secondary')


class OrderItem(models.Model):
    """Model for storing order items"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'shop.Product',
        on_delete=models.SET_NULL,
        null=True
    )
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(
        max_digits=10,
        decimal_places=0
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=0
    )
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.product_price * self.quantity
        super().save(*args, **kwargs)
