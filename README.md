# Foodgram

## О проекте

**Foodgram** — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. А список продуктов к покупке не придётся выписывать из рецептов вручную, его автоматически составит сервис «Список покупок»!

## Технологии

Backend проекта написан на **Django**, Frontend - на React.
При развертывании проекта использован **Docker**, веб-сервер **Nginx**, WSGI-сервер **Gunicorn** и БД **PostgreSQL**.
Для проекта также реализован **CI/CD** через GitHub Actions.

## Локальный запуск

- Клонируйте репозиторий
```shell
git clone <SSH ссылка на репозиторий>
```

- Создайте файл `.env`. Для этого, находясь в корне проекта, выполните:
```shell
cp .env.exemple .env
```

- Откройте `.env` и вставьте свои данные

- Перейдите в директорию `/infra` и выполните следующие команды:
```shell
docker compose build
docker compose up
```

## Автор: Муратов Максим
Backend Python Developer

![workflow](https://github.com/Maksim-Muratov/foodgram-project-react/actions/workflows/main.yml/badge.svg)
