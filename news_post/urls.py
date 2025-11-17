from django.urls import path
from .views import (
    ArticleCreateView,
    ArticleListView,
    ArticleDetailView,
    ArticleUpdateView,
    ArticleDeleteView,
    MyArticlesView,
)

urlpatterns = [
    # Public
    path("articles/", ArticleListView.as_view(), name="article-list"),
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name="article-detail"),

    # Provider-only actions
    path("create/", ArticleCreateView.as_view(), name="article-create"),
    path("my-articles/", MyArticlesView.as_view(), name="my-articles"),
    path("update/<int:pk>/", ArticleUpdateView.as_view(), name="article-update"),
    path("delete/<int:pk>/", ArticleDeleteView.as_view(), name="article-delete"),
]
