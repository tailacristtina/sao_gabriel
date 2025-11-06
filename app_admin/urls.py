from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:product_id>/', views.product_delete, name='product_delete'),
]
