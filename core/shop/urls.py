from django.urls import path

from .views import ProductListView, ProductDetailView, TestView

app_name = "shop"

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path("test/", TestView.as_view(), name="test"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
]
