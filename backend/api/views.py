from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
from django.db.models import Sum
from djoser.views import UserViewSet
from django.contrib.auth import get_user_model

from .permissions import IsAuthorOrReadOnly
from .filters import IngredientFilter, RecipeFilter
from foodgram.models import (Recipe, Follow, Tag, Ingredient, RecipeIngredient,
                             Favorite, Cart)
from .serializers import (SubscriptionSerializer, TagSerializer,
                          IngredientSerializer, FollowSerializer,
                          RecipeSerializer, CreateRecipeSerializer,
                          FavoriteSerializer, CartSerializer,)

User = get_user_model()
DEFAULT_PAGE_SIZE = 10


class CustomPagination(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'


class CustomUserViewSet(UserViewSet):
    http_method_names = ('get', 'post', 'delete',)
    pagination_class = CustomPagination

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPagination
    )
    def subscriptions(self, request, *args, **kwargs):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPagination
    )
    def subscribe(self, request, *args, **kwargs):
        followed_user = get_object_or_404(User, pk=self.kwargs.get('id'))
        serializer = FollowSerializer(
            data={'user': request.user.id, 'following': followed_user.id},
            context={'request': request}
        )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        try:
            subscription = get_object_or_404(
                Follow, user=request.user, following=followed_user)
        except Http404:
            raise ValidationError({'errors': 'Вы не подписаны'})
        subscription.delete()
        return Response(
            f'Вы отписались от {followed_user}',
            status=status.HTTP_204_NO_CONTENT
        )

    def perform_create(self, serializer):
        serializer.save()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'patch', 'delete',
                         'head', 'options', 'trace')
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        try:
            favorite = get_object_or_404(
                Favorite, user=request.user, recipe=recipe)
        except Http404:
            raise ValidationError({'errors': 'Рецепта нет в избранном'})
        favorite.delete()
        return Response(
            'Рецепт удален из избранного',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        serializer = CartSerializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        try:
            favorite = get_object_or_404(
                Cart, user=request.user, recipe=recipe)
        except Http404:
            raise ValidationError(
                {'errors': 'Рецепта нет в списке покупок'})
        favorite.delete()
        return Response(
            'Рецепт удален из списка покупок',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        '''cart_ingredients_filter = (
            RecipeIngredient.objects.filter(
                recipe__cart__user=request.user
            )
        )'''
        cart_ingredients = (
            RecipeIngredient.objects.filter(
                recipe__cart__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(cart_amount=Sum('amount'))#.order_by('-amount')
        )
        shopping_list = ''
        num = 0
        for item in cart_ingredients:
            num += 1
            name = item['ingredient__name']
            measurement_unit = item['ingredient__measurement_unit']
            measurement_unit = 'г'
            amount = item['cart_amount']
            shopping_list += (f'{num}. {name} - '
                              f'{amount} {measurement_unit} \n')
        filename = 'shopping_list.txt'
        response = HttpResponse(
            shopping_list,
            content_type='text/plain,charset=utf8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
