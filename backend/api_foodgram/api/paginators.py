from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """
    Кастомный класс пагинации
    с дополнительным параметром page_size_query_param,
    позволяющим ограничить кол-во объектов на странице.
    """
    page_size_query_param = 'limit'
