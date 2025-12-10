from django.urls import path

from .views import *
from .addresses import (
    AddressListView,
    AddressCreateView,
    AddressUpdateView,
    AddressDeleteView,
    AddressSetDefaultView,
)

app_name = "dashboard"

urlpatterns = [
    # path("addresses/", DashboardAddressesView.as_view(), name="dashboard-addresses"),
    path("orders/", DashboardOrdersView.as_view(), name="dashboard-orders"),
    path("reviews/", DashboardReviewsView.as_view(), name="dashboard-reviews"),
    path("settings/", DashboardSettingsView.as_view(), name="dashboard-settings"),
    path("wallet/", DashboardWalletView.as_view(), name="dashboard-wallet"),
    path("wishlist/", DashboardWishlistView.as_view(), name="dashboard-wishlist"),
    path("addresses/", AddressListView.as_view(), name="addresses"),
    path("addresses/add/", AddressCreateView.as_view(), name="address_add"),
    path("addresses/<int:pk>/edit/", AddressUpdateView.as_view(), name="address_edit"),
    path(
        "addresses/<int:pk>/delete/", AddressDeleteView.as_view(), name="address_delete"
    ),
    path(
        "addresses/<int:pk>/set-default/",
        AddressSetDefaultView.as_view(),
        name="address_set_default",
    ),
]
