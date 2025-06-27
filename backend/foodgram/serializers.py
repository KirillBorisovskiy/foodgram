import base64
import re

from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from djoser.serializers import TokenCreateSerializer
from rest_framework import exceptions, serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from rest_framework.authtoken.models import Token

from foodgram.models import (
    Ingredient,
    IngredientRecipe,
    Recipe,
    Tag,
    User
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class EmailAuthTokenSerializer(TokenCreateSerializer):
    def validate(self, data):
        try:
            data = super().validate(data)
            user = self.user
            token = Token.objects.get_or_create(user=user)[0]
            data['auth_token'] = token.key
            return data
        except exceptions.ValidationError:
            raise exceptions.ValidationError(
                {'error': 'Неверные учетные данные'}
            )


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=User.objects.all()
            )
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[
            UniqueValidator(
                queryset=User.objects.all()
            )
        ]
    )
    is_subscribed = serializers.SerializerMethodField()
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'password'
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=[
                    'username',
                    'email'
                ]
            )
        ]

    def validate_username(self, value):
        pattern = r'^[\w.@+-]+$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                r'Username должен содержать только буквы, цифры и @/./+/-/_'
            )
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user

    def to_representation(self, instance):
        '''Убираем поле password и поля is_subscribed/avatar при POST.'''
        data = super().to_representation(instance)
        request = self.context.get('request')
        data.pop('password', None)
        if request and request.method == 'POST' and 'users' in request.path:
            data.pop('is_subscribed', None)
            data.pop('avatar', None)
        return data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return request.user.follower.filter(author=obj).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def validate(self, data):
        data = super().validate(data)
        data = self.validate_ingredients(data)
        data = self.validate_tags(data)
        return data

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': ['Нужно выбрать ингредиент!']},
                code='required'
            )
        ingredients_list = []
        for item in ingredients:
            try:
                ingredient = Ingredient.objects.get(id=item['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    {'ingredients': [f'Ингредиент {item["id"]} не найден!']},
                    code='invalid'
                )
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    {'ingredients': ['Ингредиенты не должны повторяться!']},
                    code='duplicate'
                )
            if int(item['amount']) <= 0:
                raise serializers.ValidationError(
                    {'amount': ['Количество должно быть больше 0!']},
                    code='invalid'
                )
            ingredients_list.append(ingredient)
        data['ingredients'] = ingredients
        return data

    def validate_tags(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'tags': ['Нужно выбрать тег!']},
                code='required'
            )
        tags_list = []
        for tag_id in tags:
            try:
                tag = Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(
                    {'tags': [f'Тег с id {tag_id} не найден!']},
                    code='invalid'
                )
            if tag in tags_list:
                raise serializers.ValidationError(
                    {'tags': ['Теги не должны повторяться!']},
                    code='duplicate'
                )
            tags_list.append(tag)
        data['tags'] = tags
        return data

    def get_ingredients(self, obj):
        ingredients = obj.recipe_ingredients.select_related('ingredient')
        return [{
            'id': item.ingredient.id,
            'name': item.ingredient.name,
            'measurement_unit': item.ingredient.measurement_unit,
            'amount': item.amount
        } for item in ingredients]

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.favorited_by.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return obj.in_shopping_carts.filter(user=user).exists()

    def create(self, validated_data):
        tags_ids = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        author = self.context['request'].user
        if author.is_anonymous:
            raise exceptions.NotAuthenticated(
                detail="Для создания рецепта необходимо авторизоваться",
                code='not_authenticated'
            )
        recipe = Recipe.objects.create(
            author=author,
            **validated_data
        )

        recipe.tags.set(tags_ids)

        for ingredient in ingredients_data:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )

        return recipe

    def update(self, instance, validated_data):
        tags_ids = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        image = validated_data.pop('image', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if image is not None:
            instance.image = image

        instance.save()
        if tags_ids:
            instance.tags.set(tags_ids)
        if ingredients_data:
            instance.ingredients.clear()
            ingredients_to_create = [
                IngredientRecipe(
                    recipe=instance,
                    ingredient_id=ingredient['id'],
                    amount=ingredient['amount']
                )
                for ingredient in ingredients_data
            ]
            IngredientRecipe.objects.bulk_create(ingredients_to_create)

        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        if request and 'recipes_limit' in request.query_params:
            limit = request.query_params['recipes_limit']
            recipes = recipes[:int(limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
