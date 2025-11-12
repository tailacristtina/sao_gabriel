from django.urls import path
from . import views

urlpatterns = [
     path('', views.listar_produtos, name='listar_produtos'),
    path('carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/aumentar/<int:produto_id>/', views.aumentar_quantidade, name='aumentar_quantidade'),
    path('carrinho/diminuir/<int:produto_id>/', views.diminuir_quantidade, name='diminuir_quantidade'),
    path('carrinho/remover/<int:produto_id>/', views.remover_produto, name='remover_produto'),
     path('finalizar/', views.finalizar_pedido, name='finalizar'),
]
