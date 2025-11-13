from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views 
from users.views import carrinho_view, login_view, perfil_view # Importamos as views de Login e Perfil do app users

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('social_django.urls', namespace='social')),
    
    # PADRÕES GLOBAIS NECESSÁRIOS (Sem namespace)
    # Adicionados APENAS para que {% url 'login' %} e {% url 'perfil' %} funcionem no nav.html.
    path('login/', login_view, name='login'),
    path('perfil/', perfil_view, name='perfil'),
    
    # Inclusão principal do app 'users'. Ele mantém o namespace 'users' para uso interno.
    path('users/', include('users.urls')), 
    
    path('carrinho/', carrinho_view, name='carrinho'),
    # Página inicial agora será a listagem de produtos
    path('', include('product.urls')),
    path('checkout/', include('pagamento.urls')), 
    #paulo
    path('app_admin/', include('app_admin.urls'))
]