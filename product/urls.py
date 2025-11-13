from django.urls import path
from . import views

urlpatterns = [
     path('', views.listar_produtos, name='index'),     
     path('carrinho/', views.carrinho_view, name='carrinho_view'),
     path('adicionar/<int:product_id>/', views.adicionar_produto, name='adicionar_ao_carrinho'),
     path('carrinho/aumentar/<int:product_id>/', views.aumentar_quantidade, name='aumentar_quantidade'),
     path('carrinho/diminuir/<int:product_id>/', views.diminuir_quantidade, name='diminuir_quantidade'),
     path('carrinho/remover/<int:product_id>/', views.remover_produto, name='remover_produto'),
     path('finalizar/', views.finalizar_pedido, name='finalizar'),
     
]


 
