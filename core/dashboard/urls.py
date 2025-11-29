from django.urls import path

from .views import *

app_name = "dashboard"

urlpatterns = [
    path("addresses/", DashboardAddressesView.as_view(), name="dashboard-addresses"),
    path("orders/", DashboardOrdersView.as_view(), name="dashboard-orders"),
    path("reviews/", DashboardReviewsView.as_view(), name="dashboard-reviews"),
    path("settings/", DashboardSettingsView.as_view(), name="dashboard-settings"),
    path("wallet/", DashboardWalletView.as_view(), name="dashboard-wallet"),
    path("wishlist/", DashboardWishlistView.as_view(), name="dashboard-wishlist"),
]
