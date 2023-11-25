from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import IngredientViewSet


app_name = 'api_v1'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
]
