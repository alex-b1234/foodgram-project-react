from django.contrib import admin
from django.urls import path
from rest_framework import routers
from foodgram.views import RecipeViewSet

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
]
