from django.urls import path
from product import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('carrinho/', views.carrinho_view, name='carrinho'),
    path('', views.home_view, name='index'), 
]
