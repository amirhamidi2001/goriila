from django.urls import path
from .views import CheckoutView, OrderConfirmationView

app_name = 'order'

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('confirmation/', OrderConfirmationView.as_view(), name='order_confirmation'),
    path('confirmation/<str:order_number>/', OrderConfirmationView.as_view(), name='order_confirmation'),
]