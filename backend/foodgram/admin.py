from django.contrib import admin

from .models import (Tag, Recipe, Ingredient, Cart, Favorite, Follow,
                     RecipeIngredient, RecipeTag)

admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Favorite)
admin.site.register(Cart)
admin.site.register(Follow)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
