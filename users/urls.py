from django.urls import path
from . import views

# Defina o namespace do app users para evitar colisões
app_name = 'users' 

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    # Use 'home' como a rota principal do app users
    path('home/', views.home_view, name='home'), 
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('carrinho/', views.carrinho_view, name='carrinho'),
    # Rota para o checkout (Página de endereço/revisão)
    path('finalizar/', views.finalizar_pedido_view, name='finalizar_pedido'), 
    
    # Rota que lida com a confirmação após o Mercado Pago (se necessário, geralmente feedback é usado)
    path('confirmado/', views.pedido_confirmado_view, name='pedido_confirmado'), 
    
    # Rota base (index)
    path('', views.home_view, name='index'), 

    # ⚠️ ROTAS REMOVIDAS: 'pagamento/iniciar/' e 'feedback/'
    # Estas estão agora em 'pagamento/urls.py', acessíveis via /checkout/...
]