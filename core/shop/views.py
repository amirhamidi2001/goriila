from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import Product


class ProductListView(ListView):
    template_name = "shop/product_list.html"
    model = Product
    paginate_by = 12
    context_object_name = "products"


class ProductDetailView(DetailView):
    model = Product
    context_object_name = "product"
