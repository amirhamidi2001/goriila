from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from shop.models import Product


from django.views.generic import ListView
from django.db.models import Q
from .models import Product, Category, Brand


class ProductListView(ListView):
    model = Product
    template_name = "shop/product_list.html"
    context_object_name = "products"
    paginate_by = 12  # Optional: paginate results

    def get_queryset(self):
        queryset = super().get_queryset()

        # ✅ Search by title or description
        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )

        # ✅ Filter by category
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # ✅ Filter by brand
        brand_slug = self.request.GET.get("brand")
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)

        # ✅ Filter by availability
        available = self.request.GET.get("available")
        if available == "true":
            queryset = queryset.filter(available=True)

        # ✅ Sorting (price, created date, etc.)
        sort_by = self.request.GET.get("sort")
        if sort_by in ["price", "-price", "created_at", "-created_at", "title", "-title"]:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Provide categories & brands for sidebar filters
        context["categories"] = Category.objects.all()
        context["brands"] = Brand.objects.all()
        return context



class ShopDetailView(DetailView):
    template_name = "shop/shop_details.html"
    model = Product