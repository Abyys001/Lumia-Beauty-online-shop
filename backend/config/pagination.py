from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """Page size is client-tunable so callers can ask for a short row of products."""

    page_size_query_param = 'page_size'
    max_page_size = 48
