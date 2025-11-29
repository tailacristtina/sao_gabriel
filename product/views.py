# product/views.py

from django.shortcuts import render, redirect, get_object_or_404
# Importação local do modelo Product
from .models import Product 
# Importação do utilitário de carrinho (agora em 'store') para mostrar o total no cabeçalho
from store.utils.cart_utils import get_cart_data 


def listar_produtos(request):
    """
    Exibe a lista de todos os planos de café (Produtos).
    Esta é a view da rota base do app product.
    """
    produtos = Product.objects.all() 
    
    # O get_cart_data é usado para mostrar um resumo do carrinho no cabeçalho/menu
    cart_data = get_cart_data(request)
    
    context = {
        'produtos': produtos,
        'carrinho_subtotal': cart_data['subtotal'] 
    }
    return render(request, 'product/listar_produtos.html', context)


def detalhe_produto(request, product_id):
    """
    Exibe a página de detalhes de um único plano de café.
    """
    produto = get_object_or_404(Product, id_product=product_id)
    cart_data = get_cart_data(request)

    context = {
        'produto': produto,
        'carrinho_subtotal': cart_data['subtotal'] 
    }
    return render(request, 'product/detalhe_produto.html', context)

# Todas as outras views (carrinho, aumentar, diminuir, finalizar) foram movidas para store/views.py