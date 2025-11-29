# store/urls.py

from django.urls import path
from . import views

app_name = 'store' 

urlpatterns = [
    # Carrinho
    path('carrinho/', views.carrinho_view, name='carrinho'),
    path('carrinho/adicionar/<int:product_id>/', views.adicionar_produto, name='adicionar_ao_carrinho'),
    path('carrinho/aumentar/<int:product_id>/', views.aumentar_quantidade, name='aumentar_quantidade'),
    path('carrinho/diminuir/<int:product_id>/', views.diminuir_quantidade, name='diminuir_quantidade'),
    path('carrinho/remover/<int:product_id>/', views.remover_produto, name='remover_produto'),
    path('', views.index_home, name='index'),
    # Checkout
    path('finalizar/', views.finalizar_pedido_view, name='finalizar_pedido'), 
    
    # Feedback (Retorno do Mercado Pago)
    path('confirmado/', views.pedido_confirmado_view, name='pedido_confirmado'),
]