from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import FieldError

from .models import Product, Category, Brand, Wishlist
from .forms import ReviewForm


class ProductListView(ListView):
    """
    Display a paginated list of available products.
    """

    template_name = "shop/product_list.html"
    model = Product
    paginate_by = 12
    context_object_name = "products"

    def get_paginate_by(self, queryset):
        """
        Allow dynamic pagination size via query parameter.
        """
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        """
        Return filtered queryset of available products.
        """
        queryset = Product.objects.filter(available=True)

        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(name__icontains=search_q)

        if category_id := self.request.GET.get("category_id"):
            queryset = queryset.filter(category__id=category_id)

        if brand_id := self.request.GET.get("brand_id"):
            queryset = queryset.filter(brand__id=brand_id)

        if min_price := self.request.GET.get("min_price"):
            queryset = queryset.filter(price__gte=min_price)

        if max_price := self.request.GET.get("max_price"):
            queryset = queryset.filter(price__lte=max_price)

        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                # Ignore invalid ordering fields
                pass

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add filter metadata and total item count to context.
        """
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        context["categories"] = Category.objects.all()
        context["brands"] = Brand.objects.all()
        return context


class ProductDetailView(DetailView):
    """
    Display product details and reviews.
    """

    model = Product
    context_object_name = "product"

    def get_queryset(self):
        """
        Return the base queryset for products with related data optimized.
        """
        return (
            Product.objects.select_related("brand", "category")
            .prefetch_related("images")
            .all()
        )

    def get_context_data(self, **kwargs):
        """
        Add reviews, review form, and wishlist status to context.
        """
        context = super().get_context_data(**kwargs)
        product = self.object

        context["form"] = ReviewForm()
        context["reviews"] = product.reviews.filter(approved=True).order_by(
            "-created_at"
        )

        if self.request.user.is_authenticated:
            context["is_in_wishlist"] = Wishlist.objects.filter(
                user=self.request.user, product=product
            ).exists()
        else:
            context["is_in_wishlist"] = False

        return context

    def post(self, request, *args, **kwargs):
        """
        Handle review submission for a product.
        """
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
