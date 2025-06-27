from django_filters.rest_framework import FilterSet, filters

from foodgram.models import Recipe


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_in_shopping_cart'
    )
    author = filters.NumberFilter(field_name='author__id')
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        print("=== FILTER DEBUG ===")
        print(f"Request: {self.request}")
        print(f"User: {self.request.user}")
        print(f"Authenticated: {self.request.user.is_authenticated}")
        print(f"Value: {value}, Type: {type(value)}")

        if value and self.request.user.is_authenticated:
            print("Applying favorite filter")
            result = queryset.filter(favorited_by__user=self.request.user)
            print(f"Filtered queryset count: {result.count()}")
            return result

        print("Not applying favorite filter")
        return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(in_shopping_carts__user=user)
        return queryset
