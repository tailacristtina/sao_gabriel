from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views 
# from users.views import index, user_register, profile 


urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD
=======
    path('auth/', include('social_django.urls', namespace='social')),

>>>>>>> f59700a (#feat# + perfil funcionando)
    path('users/', include('users.urls')),
    # Página inicial agora será a listagem de produtos
    path('', include('product.urls')),
    #paulo
    path('app_admin/', include('app_admin.urls'))

]

