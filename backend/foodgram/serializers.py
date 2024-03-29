import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from .models import Recipe, Favorite, Subscribtion, User, Tag, RecipeTag


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField(
        'get_is_favorited',
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_is_favorited(self, obj):
        user = serializers.CurrentUserDefault
        user_favorite = Favorite.objects.filter(user=user)
        if user_favorite.filter(recipe=obj).exists():
            return True
        return False

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient, status = ingredients.objects.get_or_create(
                **ingredient
            )
            RecipeTag.objects.create(
                achievement=current_ingredient, recipe=recipe
            )
        return recipe


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        field = ('name', 'color', 'slug')
        model = Tag


class SubscribtiionSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    following = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        fields = ('user', 'subscribing')
        model = Subscribtion
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribtion.objects.all(),
                fields=('user', 'subscribing'),
                message='Уже подписаны'
            )
        ]

    def validate_following(self, data):
        if self.context.get('request').user == data:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя.'
            )
        if not User.objects.get(username=data):
            raise serializers.ValidationError('Пользователь не существует.')
        return data
