from django.contrib.sitemaps import Sitemap
from .models import Post


class BlogSitemap(Sitemap):
    # How often the page is likely to change
    changefreq = "weekly"
    # Priority relative to other URLs on your site (0.0 to 1.0)
    priority = 0.7

    def items(self):
        # We only want to index posts that are published (status=True)
        return Post.objects.filter(status=True)

    def lastmod(self, obj):
        # Tells search engines when the post was last updated
        return obj.updated_at
