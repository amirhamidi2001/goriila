from django import template
from blog.models import Post

register = template.Library()


@register.inclusion_tag("blog/blog_hero.html")
def blog_hero(count=5):
    """
    Returns the blog hero published posts.
    """
    blog_hero = Post.objects.filter(status=True).order_by("-published_at")[:count]
    return {"blog_hero": blog_hero}


@register.inclusion_tag("blog/latest_posts.html")
def latest_posts(count=4):
    """
    Returns the blog hero published posts.
    """
    latest_posts = Post.objects.filter(status=True).order_by("-published_at")[:count]
    return {"latest_posts": latest_posts}
