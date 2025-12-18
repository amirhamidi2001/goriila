from django.contrib.sitemaps import Sitemap
from .models import Product, Category, Brand


class ProductSitemap(Sitemap):
    changefreq = "daily"  # Prices and stock change often
    priority = 0.9  # Products are your most important pages

    def items(self):
        # Only index products that are marked as available
        return Product.objects.filter(available=True)

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Category.objects.filter(is_active=True)


class BrandSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Brand.objects.filter(is_active=True)
