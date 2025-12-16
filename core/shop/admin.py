from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, Brand, Review, Wishlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


class ImagePreviewMixin:
    """Reusable image preview mixin."""

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" style="border-radius:4px;" />',
                obj.image.url,
            )
        return "—"

    image_preview.short_description = "Image"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = (
        "name",
        "category",
        "brand",
        "price",
        "discount",
        "stock",
        "in_stock",
        "available",
        "image_preview",
    )
    list_filter = ("available", "category", "brand", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at", "image_preview", "hologram_preview")
    autocomplete_fields = ("category", "brand")

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "category",
                    "brand",
                    "description",
                    "breif_description",
                )
            },
        ),
        (
            "Pricing & Availability",
            {"fields": ("price", "discount", "stock", "available")},
        ),
        (
            "Images",
            {"fields": ("image", "image_preview", "hologram", "hologram_preview")},
        ),
        ("Detail", {"fields": ("weight", "taste", "rating", "especial")}),
        ("Metadata", {"fields": ("created_at", "updated_at")}),
    )

    def hologram_preview(self, obj):
        if obj.hologram:
            return format_html(
                '<img src="{}" width="60" style="border-radius:4px;" />',
                obj.hologram.url,
            )
        return "—"

    hologram_preview.short_description = "Hologram"

    ordering = ("-created_at",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for Review model.
    """

    list_display = ("name", "product", "approved", "created_at")
    list_filter = ("approved",)
    search_fields = ("name", "email", "review")
    actions = ["approve_reviews"]
