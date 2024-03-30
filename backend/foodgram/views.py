from rest_framework import viewsets, mixins, permissions, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from djoser.views import UserViewSet

from .models import Recipe, Subscribtion, Tag, Ingredient, RecipeIngredient
from .permissions import IsAuthorOrReadOnly
from .serializers import (RecipeListSerializer, SubscribtiionSerializer,
                          TagSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer)


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', ]
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def get_queryset(self):
        qs = Recipe.objects.add_user_annotations(self.request.user.pk)
        author = self.request.query_params.get('author', None)
        if author:
            qs = qs.filter(author=author)
        return qs


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


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
