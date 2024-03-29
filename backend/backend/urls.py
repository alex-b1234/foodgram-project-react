from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from foodgram.views import RecipeViewSet, TagViewSet

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include('djoser.urls')),
]
