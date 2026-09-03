from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ProductViewSet,
    place_order,
    get_product_reviews,
    submit_review,
)

router = DefaultRouter()

router.register(
    r"categories",
    CategoryViewSet,
    basename="category",
)

router.register(
    r"products",
    ProductViewSet,
    basename="product",
)


urlpatterns = [
    # REST API
    path(
        "",
        include(router.urls),
    ),

    # Orders
    path(
        "place-order/",
        place_order,
        name="place_order",
    ),

    # Reviews
    path(
        "reviews/<int:product_id>/",
        get_product_reviews,
        name="get_product_reviews",
    ),

    path(
        "reviews/<int:product_id>/submit/",
        submit_review,
        name="submit_review",
    ),
]