from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from django.shortcuts import redirect
from django.contrib import messages

from .models import Product, Review
from .forms import ReviewForm


class ProductListView(ListView):
    template_name = "shop/product_list.html"
    model = Product
    paginate_by = 12
    context_object_name = "products"

    def get_queryset(self):
        queryset = Product.objects.filter(available=True)
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        brand_slug = self.request.GET.get("brand")
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)

        sort_option = self.request.GET.get("sort", "")
        if sort_option == "price_asc":
            queryset = queryset.order_by("price")
        elif sort_option == "price_desc":
            queryset = queryset.order_by("-price")
        elif sort_option == "name_asc":
            queryset = queryset.order_by("name")
        elif sort_option == "name_desc":
            queryset = queryset.order_by("-name")
        elif sort_option == "newest":
            queryset = queryset.order_by("-created_at")

        return queryset

class ProductDetailView(DetailView):
    model = Product
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        context["form"] = ReviewForm()

        context["reviews"] = product.reviews.filter(approved=True).order_by(
            "-created_at"
        )

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.product = self.object
            review.save()
            messages.success(self.request, "نظر شما با موفقیت ارسال شد")
            return redirect(self.request.path_info)

        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)
