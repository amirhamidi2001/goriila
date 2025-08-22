from django.urls import path

from shop.views import ProductListView, ShopDetailView

app_name = "shop"

urlpatterns = [
    path("", ProductListView.as_view(), name="shop"),
    path("products/<slug:slug>/", ShopDetailView.as_view(), name="product_detail"),
]
