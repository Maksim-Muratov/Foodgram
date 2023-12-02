from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, TagViewSet


app_name = 'api_v1'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
]
