from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from store.views import (
    home_view, register_view, place_order, orders_view,
    farmer_dashboard_view, add_farmer_product, toggle_product_status, delete_farmer_product,
    driver_dashboard_view, accept_order, driver_portal_view,
    update_driver_location, get_driver_location,
    submit_review, get_product_reviews
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('my-orders/', orders_view, name='my_orders'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register_view, name='register'),
    path('api/place-order/', place_order, name='place_order'),
    
    # Farmer Portal Endpoints
    path('farmer/dashboard/', farmer_dashboard_view, name='farmer_dashboard'),
    path('api/farmer/add-product/', add_farmer_product, name='add_farmer_product'),
    path('api/farmer/toggle-status/<int:product_id>/', toggle_product_status, name='toggle_product_status'),
    path('api/farmer/delete-product/<int:product_id>/', delete_farmer_product, name='delete_farmer_product'),

    # Product Reviews
    path('api/reviews/<int:product_id>/', get_product_reviews, name='get_product_reviews'),
    path('api/reviews/<int:product_id>/submit/', submit_review, name='submit_review'),

    # Driver Portal & GPS Tracking
    path('driver/dashboard/', driver_dashboard_view, name='driver_dashboard'),
    path('api/accept-order/<int:order_id>/', accept_order, name='accept_order'),
    path('driver/<int:order_id>/', driver_portal_view, name='driver_portal'),
    path('api/update-driver-location/', update_driver_location, name='update_driver_location'),
    path('api/get-driver-location/<int:order_id>/', get_driver_location, name='get_driver_location'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')