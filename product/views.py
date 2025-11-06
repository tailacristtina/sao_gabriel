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

from django.shortcuts import render, redirect
from .models import Product
from django.contrib import messages

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

    # Inicializa frete
    frete = request.session.get('frete', 0)
    cep_informado = request.session.get('cep', '')

    # Se o usuário enviar o CEP
    if request.method == 'POST' and 'cep' in request.POST:
        cep = request.POST['cep']
        frete = calcular_frete_fake(cep)
        request.session['frete'] = frete
        request.session['cep'] = cep
        total += frete
        messages.info(request, f"Frete para o CEP {cep}: R$ {frete:.2f}")
    else:
        total += frete  # soma o frete salvo, se existir

    return render(request, 'product/carrinho.html', {
        'itens': itens,
        'total': total,
        'frete': frete,
        'cep': cep_informado
    })


def calcular_frete_fake(cep):
    """Simulação de cálculo de frete com base no prefixo do CEP"""
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


from users.models import Users
from .models import Product, Pedido, ItemPedido

def finalizar_pedido(request):
    if 'user_id' not in request.session:
        # se o usuário não estiver logado, redireciona pro login
        return redirect('login')

    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('ver_carrinho')

    user_id = request.session['user_id']
    usuario = Users.objects.get(id_users=user_id)
    produtos = Product.objects.filter(id_product__in=carrinho.keys())

    total = 0
    pedido = Pedido.objects.create(usuario=usuario, total=0)

    for produto in produtos:
        quantidade = carrinho[str(produto.id_product)]
        subtotal = produto.price * quantidade
        ItemPedido.objects.create(
            pedido=pedido,
            produto=produto,
            quantidade=quantidade,
            subtotal=subtotal
        )
        total += subtotal

    pedido.total = total
    pedido.save()

    # limpa o carrinho após salvar
    request.session['carrinho'] = {}

    messages.success(request, f"Pedido {pedido.id_pedido} realizado com sucesso!")
    return render(request, 'product/pedido_confirmado.html', {'pedido': pedido})
