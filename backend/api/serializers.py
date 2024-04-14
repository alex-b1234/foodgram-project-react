from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from django.contrib.auth import get_user_model

from foodgram.models import (Recipe, Follow, Ingredient, Favorite,
                             Tag, RecipeTag, RecipeIngredient, Cart)

User = get_user_model()
DEFAULT_PAGE_SIZE = 10


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'last_name', 'is_subscribed',
                  'first_name', 'username', 'password',)
        extra_kwargs = {
            'password': {'write_only': True},
            'is_subscribed': {'read_only': True}
        }

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, following=obj.id).exists()

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(read_only=True, many=True,
                                             source='recipe_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Cart.objects.filter(
            recipe=obj, user=request.user).exists()


class SubRecipeSerializer:

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return SubRecipeSerializer(
            instance=instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return SubRecipeSerializer(
            instance=instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit', DEFAULT_PAGE_SIZE)
        recipes = obj.recipes.all()[:int(recipes_limit)]
        serializer = SubRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message=('Вы уже подписаны')
            ),
        )

    def validate(self, data):
        if data.get('user') == data.get('following'):
            raise serializers.ValidationError(
                {'errors': 'Вы не можете подписаться на себя.'})
        return data

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance=instance.following,
            context={'request': self.context.get('request')}
        ).data


class CreateRecipeIngredientSerializer(RecipeIngredientSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = CreateRecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'tags', 'ingredients', 'name', 'image', 'text', 'cooking_time'
        )

    def to_representation(self, instance):
        return RecipeSerializer(
            instance=instance,
            context={'request': self.context.get('request')}
        ).data

    def add_tags_ingredients(self, ingredients, tags, model):
        recipeingredients_data = []
        for ingredient in ingredients:
            recipeingredients_data.append(RecipeIngredient(
                recipe=model,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ))
        RecipeIngredient.objects.bulk_create(recipeingredients_data)

        recipetags_data = []
        for tag in tags:
            recipetags_data.append(RecipeTag(recipe=model, tag=tag))
        RecipeTag.objects.bulk_create(recipetags_data)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        self.add_tags_ingredients(ingredients, tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        self.add_tags_ingredients(ingredients, tags, instance)
        return super().update(instance, validated_data)
