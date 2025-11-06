from django.shortcuts import render, redirect
from .models import Product

def listar_produtos(request):
    produtos = Product.objects.all()
    return render(request, 'product/listar_produtos.html', {'produtos': produtos})

def adicionar_ao_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    carrinho[str(produto_id)] = carrinho.get(str(produto_id), 0) + 1
    request.session['carrinho'] = carrinho
    return redirect('listar_produtos')

def ver_carrinho(request):
    carrinho = request.session.get('carrinho', {})
    produtos = Product.objects.filter(id_product__in=carrinho.keys())

    itens = []
    total = 0
    for produto in produtos:
        quantidade = carrinho[str(produto.id_product)]
        subtotal = produto.price * quantidade
        total += subtotal
        itens.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal
        })

    return render(request, 'product/carrinho.html', {'itens': itens, 'total': total})
