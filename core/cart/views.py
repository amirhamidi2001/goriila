from django.views.generic.base import TemplateView


class CartView(TemplateView):
    template_name = "cart/cart.html"
