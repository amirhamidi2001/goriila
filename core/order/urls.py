from django.urls import path
from . import views

app_name = "order"

urlpatterns = [
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("confirmation/", views.OrderConfirmationView.as_view(), name="confirmation"),
    path(
        "shipping-invoices/",
        views.ShippingInvoiceListView.as_view(),
        name="shipping_invoice_list",
    ),
    path(
        "shipping-invoice/<int:order_id>/",
        views.ShippingInvoiceDetailView.as_view(),
        name="shipping_invoice_detail",
    ),
    path(
        "shipping-invoice/<int:order_id>/pdf/",
        views.shipping_invoice_pdf_view,
        name="shipping_invoice_pdf",
    ),
]
