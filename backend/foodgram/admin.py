from django.contrib import admin

from .models import (Tag, Recipe, Ingredient,
                     RecipeIngredient, Favorite, Subscribtion)

admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(Subscribtion)
