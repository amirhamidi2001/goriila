from django.urls import path
from . import views

app_name = "order"

urlpatterns = [
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("confirmation/", views.OrderConfirmationView.as_view(), name="confirmation"),
]
