from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import FieldError

from .models import Product, Category, Brand
from .forms import ReviewForm


class ProductListView(ListView):
    template_name = "shop/product_list.html"
    model = Product
    paginate_by = 12
    context_object_name = "products"

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
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
                pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        context["categories"] = Category.objects.all()
        context["brands"] = Brand.objects.all()
        return context


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


from django.views.generic.base import TemplateView


class TestView(TemplateView):
    template_name = "shop/test.html"
