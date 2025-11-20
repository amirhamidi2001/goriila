from django import template
from shop.models import Product

register = template.Library()


@register.inclusion_tag("shop/best_sellers.html")
def best_sellers(count=4):
    """
    Returns the blog hero published posts.
    """
    best_sellers = Product.objects.filter(available=True).order_by("created_at")[:count]
    return {"best_sellers": best_sellers}


@register.inclusion_tag("shop/call_action.html")
def call_action(count=4):
    """
    Returns the blog hero published posts.
    """
    call_action = Product.objects.filter(available=True).order_by("-discount")[:count]

    return {"call_action": call_action}


@register.inclusion_tag("shop/latest_products.html")
def latest_products(count=3):
    """
    Returns the blog hero published posts.
    """
    latest_products = Product.objects.filter(available=True).order_by("-created_at")[
        :count
    ]
    return {"latest_products": latest_products}


@register.inclusion_tag("shop/best_products.html")
def best_products(count=3):
    """
    Returns the blog hero published posts.
    """
    best_products = Product.objects.filter(available=True).order_by("created_at")[
        :count
    ]
    return {"best_products": best_products}


@register.inclusion_tag("shop/especial_products.html")
def especial_products(count=3):
    """
    Returns the blog hero published posts.
    """
    especial_products = Product.objects.filter(available=True).order_by("-rating")[
        :count
    ]
    return {"especial_products": especial_products}
