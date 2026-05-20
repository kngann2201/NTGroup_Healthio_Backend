from rest_framework.pagination import PageNumberPagination

class ExercisePaginators(PageNumberPagination):
    page_size = 5

class DishPaginators(PageNumberPagination):
    page_size = 6