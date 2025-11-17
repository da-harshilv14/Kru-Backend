from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied

from .models import Article
from .serializers import ArticleSerializer
from .permissions import IsSubsidyProvider


class ArticleCreateView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsSubsidyProvider]
    parser_classes = (MultiPartParser, FormParser)


class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.all().order_by("-created_at")
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()

        # Optional limit: /news/articles/?limit=3 or ?limit=10
        limit = self.request.query_params.get("limit")
        if limit:
            return qs[:int(limit)]

        return qs


class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]


class MyArticlesView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsSubsidyProvider]

    def get_queryset(self):
        return Article.objects.filter(provider=self.request.user)


class ArticleUpdateView(generics.UpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsSubsidyProvider]
    parser_classes = (MultiPartParser, FormParser)

    def perform_update(self, serializer):
        article = self.get_object()
        user = self.request.user

        if user != article.provider and user.role != "admin":
            raise PermissionDenied("You cannot update this article.")

        serializer.save()


class ArticleDeleteView(generics.DestroyAPIView):
    queryset = Article.objects.all()
    permission_classes = [IsSubsidyProvider]

    def perform_destroy(self, instance):
        user = self.request.user

        if user != instance.provider and user.role != "admin":
            raise PermissionDenied("You cannot delete this article.")

        instance.delete()
