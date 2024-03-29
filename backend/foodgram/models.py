from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=16)
    slug = models.SlugField(max_length=64, unique=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=50)


class Recipe(models.Model):
    name = models.CharField(max_length=50)
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to='foodgram/images/',
        null=True,
        default=None
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField()
    measurement_unit = models.CharField(max_length=20)


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE)


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE
    )


class Subscribtion(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user')
    subscribing = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribing')
