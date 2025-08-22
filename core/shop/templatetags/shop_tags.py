from django import template
from shop.models import Product

register = template.Library()

@register.inclusion_tag("shop/latest_product.html")
def recent_products(count=9):
    """
    Retrieve 'count' number of recent products (default: 9).
    """
    products = Product.objects.filter(available=True).order_by("-created_at")[:count]
    return {"products": products}
