Foodgram - "Продуктовый помощник"
Описание
Foodgram - это сайт, где пользователи могут:

Публиковать свои рецепты

Добавлять понравившиеся рецепты в избранное

Подписываться на других авторов

Формировать корзину покупок с ингредиентами для выбранных рецептов

Развертывание проекта (Fork & Deployment)
1. Форк репозитория
Перейдите на репозиторий проекта

Нажмите кнопку "Fork" в правом верхнем углу

Выберите свой аккаунт в качестве места для форка

2. Клонирование репозитория
bash
git clone https://github.com/ваш-username/foodgram.git
cd foodgram
3. Настройка окружения
Создайте файл .env в директории infra/ со следующим содержанием:

text
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

SECRET_KEY=ваш-secret-key
ALLOWED_HOSTS=backend,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1,

4. Запуск с помощью Docker
Убедитесь, что у вас установлены Docker и docker-compose

Выполните команды:

bash
cd infra/
docker-compose up -d
После запуска контейнеров выполните миграции:

bash
docker-compose exec backend python manage.py migrate
Создайте суперпользователя:

bash
docker-compose exec backend python manage.py createsuperuser
При необходимости загрузите ингредиенты в БД:

bash
docker-compose exec backend python manage.py load_ingredients
5. Доступ к проекту
После успешного развертывания проект будет доступен по адресу:

Проект:
http://localhost/

Админка:
http://localhost/admin/
Технологии
Python 3.9

Django 3.2

Django REST Framework

PostgreSQL

Nginx

Docker

Gunicorn

Автор
Кирилл Борисовский
