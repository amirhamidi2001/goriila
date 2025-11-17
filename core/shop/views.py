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
