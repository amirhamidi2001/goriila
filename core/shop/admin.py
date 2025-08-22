from django.contrib import admin
from shop.models import Category, Brand, Product, ProductImage  # , ShoppingCart


class CategoryAdmin(admin.ModelAdmin):
    """
    This class is used to customize the appearance and functionality of the Category model in the Django admin interface.
    """

    list_display = ("title", "slug")
    list_filter = ("title", "slug")
    search_fields = ("title", "slug")
    prepopulated_fields = {'slug': ('title',)}


class BrandAdmin(admin.ModelAdmin):
    """
    This class is used to customize the appearance and functionality of the Brand model in the Django admin interface.
    """

    list_display = ("title", "slug")
    list_filter = ("title", "slug")
    search_fields = ("title", "slug")
    # prepopulated_fields = {'slug': ('title',)}


class ProductAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ('title', 'slug', 'price', 'available', 'stock', 'created_at', 'updated_at')
    list_filter = ('available', 'category', 'brand')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    empty_value_display = '-empty-'


class ProductImageAdmin(admin.ModelAdmin):
    """
    This class is used to customize the appearance and functionality of the ProductImage model in the Django admin interface
    """

    list_display = ("get_product_title", "get_product_slug")

    def get_product_title(self, obj):
        return obj.product.title

    def get_product_slug(self, obj):
        return obj.product.slug

admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
