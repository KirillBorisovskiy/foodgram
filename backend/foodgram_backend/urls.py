from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from djoser.views import (
    TokenCreateView,
    TokenDestroyView,
)
from rest_framework import routers

from foodgram.views import (
    IngredientViewSet,
    RecipeViewSet,
    short_url_redirect,
    TagViewSet,
    UserViewSet
)


router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),  # Работа с пользователями
    path(
        'api/auth/token/login/',
        TokenCreateView.as_view(),
        name='login'
    ),
    path(
        'api/auth/token/logout/',
        TokenDestroyView.as_view(),
        name='logout'
    ),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
    path('s/<str:code>/', short_url_redirect, name='recipe-short-link')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
