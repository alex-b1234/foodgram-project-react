from typing import Optional

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200, blank=False,
                            unique=True, db_index=True
                            )
    color = models.CharField(
        max_length=10, unique=True
    )
    slug = models.SlugField(
        max_length=200, null=True, unique=True
    )


class Ingredient(models.Model):
    name = models.CharField(max_length=50)
    measurement_unit = models.CharField(
        max_length=200
    )

    def __str__(self):
        return self.name


class RecipeQuerySet(models.QuerySet):
    def add_user_annotations(self, user_id: Optional[int]):
        return self.annotate(
            in_shopping_cart=models.Exists(
                Cart.objects.filter(
                    user_id=user_id, recipe__pk=models.OuterRef('pk')
                )
            ),
            in_favorite=models.Exists(
                Favorite.objects.filter(
                    user_id=user_id, recipe__pk=models.OuterRef('pk')
                )
            )
        )


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
    )
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    cooking_time = models.PositiveSmallIntegerField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    image = models.ImageField(
        upload_to='foodgram/images/',
        null=True,
        default=None
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ('-pub_date', )
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique_author_recipe'
            ),
        ]

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'{self.user} {self.recipe}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_user_recipe'
            )
        ]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_follow'
            ),
        ]
