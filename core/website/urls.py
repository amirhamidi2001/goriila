"""URL configuration for the website app."""

from django.urls import path

from .views import AboutView, ContactView, Custom404View, FAQView, IndexView

app_name = "website"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("about/", AboutView.as_view(), name="about"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("faq/", FAQView.as_view(), name="faq"),
]
