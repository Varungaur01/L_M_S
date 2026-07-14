from django.urls import path
from . import views

urlpatterns = [
    path('', views.explore, name='explore'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/add/', views.add_product, name='add_product'),
    
    # Cart & Checkout
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/assign/<int:order_id>/', views.assign_order, name='assign_order'),
    
    # Delivery
    path('delivery/', views.delivery_dashboard, name='delivery_dashboard'),
    path('delivery/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
]
