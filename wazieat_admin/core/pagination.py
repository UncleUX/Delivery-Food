"""Docstring for file."""
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Docstring for class."""

    page_size_query_param = 'size'  # items per page
