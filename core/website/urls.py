from django.urls import path

from website.views import IndexView, AboutView, ContactView, NewsletterSubscribeView

app_name = "website"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("about/", AboutView.as_view(), name="about"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("newsletter/", NewsletterSubscribeView.as_view(), name="newsletter"),
]
