from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from foodgram.models import Ingredient, Recipe, Tag

User = get_user_model()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
    )
    empty_value_display = '-пусто-'


@admin.register(User)
class AdminUser(UserAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('email', 'username',)
    list_filter = ('email', 'username',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngridiendAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
    )
    search_fields = ('author', 'name',)
    list_filter = ('tags',)
    empty_value_display = '-пусто-'


admin.site.unregister(Group)
