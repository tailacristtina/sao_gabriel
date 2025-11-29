from django.contrib import admin
from django.urls import path, include
from product import views as product_views

urlpatterns = [
    path('', include('store.urls')),    
    # Rotas dos Apps
    path('users/', include('users.urls')),
    path('products/', include('product.urls')),
    path('store/', include('store.urls')),
    path('payment/', include('payment.urls')),
    path('app_admin/', include('app_admin.urls')),
        
    # Admin
    path('admin/', admin.site.urls),
]