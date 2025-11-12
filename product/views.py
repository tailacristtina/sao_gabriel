from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product, Order, ItemPedido
from users.models import Users

# 🛒 LISTAR PRODUTOS
def listar_produtos(request):
    produtos = Product.objects.all()
    return render(request, 'product/listar_produtos.html', {'produtos': produtos})


# ➕ ADICIONAR AO CARRINHO
def adicionar_ao_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    carrinho[str(produto_id)] = carrinho.get(str(produto_id), 0) + 1
    request.session['carrinho'] = carrinho
    messages.success(request, "Produto adicionado ao carrinho!")
    return redirect('listar_produtos')


# 📦 VISUALIZAR CARRINHO
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

    # Calcular frete
    frete = request.session.get('frete', 0)
    cep_informado = request.session.get('cep', '')

    if request.method == 'POST' and 'cep' in request.POST:
        cep = request.POST['cep']
        frete = calcular_frete_fake(cep)
        request.session['frete'] = frete
        request.session['cep'] = cep
        messages.info(request, f"Frete para o CEP {cep}: R$ {frete:.2f}")
    else:
        total += frete

    total += frete

    return render(request, 'product/carrinho.html', {
        'itens': itens,
        'total': total,
        'frete': frete,
        'cep': cep_informado
    })


# ➕ AUMENTAR QUANTIDADE
def aumentar_quantidade(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    produto_id = str(produto_id)
    carrinho[produto_id] = carrinho.get(produto_id, 0) + 1
    request.session['carrinho'] = carrinho
    messages.success(request, "Quantidade aumentada!")
    return redirect('ver_carrinho')


# ➖ DIMINUIR QUANTIDADE
def diminuir_quantidade(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    produto_id = str(produto_id)
    if produto_id in carrinho:
        if carrinho[produto_id] > 1:
            carrinho[produto_id] -= 1
        else:
            carrinho.pop(produto_id)
    request.session['carrinho'] = carrinho
    messages.info(request, "Quantidade atualizada!")
    return redirect('ver_carrinho')


# ❌ REMOVER PRODUTO
def remover_produto(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    produto_id = str(produto_id)
    if produto_id in carrinho:
        carrinho.pop(produto_id)
    request.session['carrinho'] = carrinho
    messages.warning(request, "Produto removido do carrinho!")
    return redirect('ver_carrinho')


# 🚚 FRETE FAKE
def calcular_frete_fake(cep):
    if cep.startswith('01'):   # SP
        return 10.0
    elif cep.startswith('20'):  # RJ
        return 15.0
    elif cep.startswith('30'):  # MG
        return 18.0
    elif cep.startswith('70'):  # DF
        return 20.0
    else:
        return 25.0

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from users.models import Users
from .models import Order, OrderItem
from django.contrib.auth import get_user

@login_required(login_url='/login/')
def finalizar_pedido(request):
    user = get_user(request)

    # Verifica se o carrinho está na sessão
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.warning(request, "Seu carrinho está vazio.")
        return redirect('carrinho')

    # Cria o pedido
    order = Order.objects.create(
        user=user,
        total=0,
        status='Pendente'
    )

    total = 0
    for produto_id, item in carrinho.items():
        quantidade = item['quantidade']
        subtotal = float(item['preco']) * quantidade
        total += subtotal

        OrderItem.objects.create(
            order=order,
            product_id=produto_id,
            quantity=quantidade,
            subtotal=subtotal
        )

    order.total = total
    order.save()

    # Limpa o carrinho
    del request.session['carrinho']

    # Redireciona para a página de pagamento
    return redirect('pagamento', order_id=order.id_order)


import mercadopago
from django.conf import settings
from django.http import JsonResponse

@login_required(login_url='/login/')
def pagamento(request, order_id):
    order = Order.objects.get(id_order=order_id)
    items = []

    for item in order.itens.all():
        items.append({
            "title": item.product.name,
            "quantity": int(item.quantity),
            "currency_id": "BRL",
            "unit_price": float(item.subtotal / item.quantity)
        })

    sdk = mercadopago.SDK("SUA_ACCESS_TOKEN_AQUI")

    preference_data = {
        "items": items,
        "back_urls": {
            "success": "http://127.0.0.1:8000/pedido/sucesso/",
            "failure": "http://127.0.0.1:8000/pedido/erro/",
            "pending": "http://127.0.0.1:8000/pedido/pendente/",
        },
        "auto_return": "approved",
        "external_reference": str(order.id_order)
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]

    return render(request, "product/pagamento.html", {
        "preference_id": preference["id"],
        "order": order
    })
