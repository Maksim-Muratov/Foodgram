from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Пагинация для отображения пользователей."""

    page_query_param = 'page'
    page_size_query_param = 'limit'
