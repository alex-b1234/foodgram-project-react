from rest_framework import viewsets, mixins, permissions, filters
from rest_framework.pagination import PageNumberPagination

from .models import Recipe, Subscribtion, Tag
from .serializers import RecipeSerializer, SubscribtiionSerializer, TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ViewSet):
    queryset = Tag.objects.all()
    serializer_class = RecipeSerializer


class SubscribtionViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                          mixins.CreateModelMixin,):
    serializer_class = SubscribtiionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('subscribing__username',)

    def get_queryset(self):
        queryset = Subscribtion.objects.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
