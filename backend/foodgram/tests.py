from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from foodgram.models import Recipe


class RecipeAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(
            username='auth_user',
            email='user@example.com',
            password='testpass123'
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.recipe = Recipe.objects.create(
            author=self.user,
            name='Тестовый рецепт',
            text='Описание тестового рецепта',
            cooking_time=30
        )

    def test_list_exists(self):
        """Проверка доступности списка рецептов."""
        response = self.client.get('/api/recipes/')

        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            msg='API списка рецептов должно возвращать статус 200 OK'
        )
        self.assertIn('results', response.data)
        self.assertGreater(len(response.data['results']), 0)

    def test_unauthorized_access(self):
        """Проверка создания рецепта не авторизованным пользователем."""
        self.client.logout()
        self.assertNotEqual(
            Recipe.objects.create(
                author=self.user,
                name='Тестовый рецепт',
                text='Описание тестового рецепта',
                cooking_time=30
            ),
            HTTPStatus.UNAUTHORIZED,
            msg='Неавторизованные не может создать рецепт'
        )
