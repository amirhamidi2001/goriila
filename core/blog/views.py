from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import redirect
from django.contrib import messages

from .models import Post
from .forms import CommentForm


class PostListView(ListView):
    """
    Displays a paginated list of blog posts with optional filtering.
    """

    model = Post
    paginate_by = 12
    context_object_name = "posts"
    template_name = "blog/post_list.html"


class PostDetailView(LoginRequiredMixin, DetailView):
    """
    Displays the detailed view of a single blog post, including comments and navigation.
    """

    model = Post
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        post.counted_views += 1
        post.save(update_fields=["counted_views"])

        context["form"] = CommentForm()

        context["comments"] = post.comments.filter(approved=True).order_by(
            "-created_at"
        )

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.save()
            messages.success(self.request, "نظر شما با موفقیت ارسال شد")
            return redirect(self.request.path_info)

        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)
