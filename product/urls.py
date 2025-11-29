# product/urls.py

from django.urls import path
from . import views

app_name = 'product' # Definir um namespace é uma boa prática

urlpatterns = [
    # 1. Rota para listar todos os produtos
    path('', views.listar_produtos, name='listar_produtos'), 
    
    # 2. Rota para ver os detalhes de um produto específico
    path('<int:product_id>/', views.detalhe_produto, name='detalhe_produto'),
]