from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from accounts.validators import validate_iranian_cellphone_number


User = get_user_model()


def validate_image_size(image):
    max_size = 2 * 1024 * 1024  # 2MB
    if image.size > max_size:
        raise ValidationError("حجم عکس نباید بیشتر از ۲ مگابایت باشه")


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
        max_length=200,
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
    postal_code = models.CharField(max_length=200, verbose_name="Postal Code")
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

    ORDER_STATUS_CHOICES = (
        ("pending", "در انتظار بررسی"),
        ("payment_verified", "پرداخت تایید شده"),
        ("processing", "در حال پردازش"),
        ("shipped", "ارسال شده"),
        ("delivered", "تحویل داده شده"),
        ("cancelled", "لغو شده"),
    )

    # User and cart reference
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders", verbose_name="کاربر"
    )

    # Order number (unique identifier)
    order_number = models.CharField(
        max_length=200, unique=True, editable=False, verbose_name="شماره سفارش"
    )

    # Shipping address (copied from Address model)
    shipping_full_name = models.CharField(max_length=200, verbose_name="نام گیرنده")
    shipping_phone = models.CharField(max_length=12, verbose_name="شماره تماس")
    shipping_address_line1 = models.CharField(max_length=255, verbose_name="آدرس خط 1")
    shipping_address_line2 = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="آدرس خط 2"
    )
    shipping_city = models.CharField(max_length=100, verbose_name="شهر")
    shipping_state = models.CharField(max_length=100, verbose_name="استان")
    shipping_postal_code = models.CharField(max_length=200, verbose_name="کد پستی")
    shipping_country = models.CharField(
        max_length=100, default="ایران", verbose_name="کشور"
    )

    # Payment receipt
    payment_receipt = models.ImageField(
        upload_to="payment_receipts/%Y/%m/%d/",
        validators=[validate_image_size],
        verbose_name="رسید پرداخت",
    )

    # Order totals
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name="جمع جزء"
    )
    shipping_cost = models.DecimalField(
        max_digits=10, decimal_places=0, default=0, verbose_name="هزینه ارسال"
    )
    total = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="جمع کل")

    # Order status
    status = models.CharField(
        max_length=200,
        choices=ORDER_STATUS_CHOICES,
        default="pending",
        verbose_name="وضعیت سفارش",
    )

    # Additional notes
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")

    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"
        ordering = ["-created_date"]

    def __str__(self):
        return f"سفارش #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            import random
            import string
            from django.utils import timezone

            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            random_str = "".join(random.choices(string.digits, k=4))
            self.order_number = f"ORD{timestamp}{random_str}"

        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Model for storing order items"""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="سفارش"
    )
    product = models.ForeignKey(
        "shop.Product", on_delete=models.CASCADE, verbose_name="محصول"
    )
    product_name = models.CharField(max_length=255, verbose_name="نام محصول")
    product_price = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name="قیمت محصول"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name="جمع جزء"
    )

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
