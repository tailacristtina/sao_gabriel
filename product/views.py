# product/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import mercadopago
import json

# =========================================================
# IMPORTAÇÕES CORRETAS DOS SEUS MODELOS E UTILITÁRIOS
# =========================================================
from .models import Order, ItemPedido, Product 
from app_admin.models import Users 
from .utils.cart_utils import get_cart_data, add_to_cart 
# =========================================================

# --- FUNÇÃO DE SERVIÇO MP ---
def criar_preferencia_mercadopago(order, itens):
    """Cria a preferência de pagamento no Mercado Pago."""
    # (Corpo da função MP, como na resposta anterior)
    try:
        sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

        preference_data = {
            "items": itens,
            "payer": {
                "email": order.user.email, 
            },
            "shipments": {
                "cost": float(order.shipping_value),
                "mode": "not_specified", 
            },
            "external_reference": str(order.id_order), 
            # ATUALIZE COM SUAS URLS REAIS
            "notification_url": "https://SEU_DOMINO/webhooks/mercadopago/", 
            "back_urls": {
                "success": f"https://SEU_DOMINO/pedidos/confirmado/{order.id_order}/", 
                "pending": f"https://SEU_DOMINO/pedidos/pendente/{order.id_order}/",
                "failure": f"https://SEU_DOMINO/pedidos/falha/{order.id_order}/",
            },
            "auto_return": "approved", 
        }

        preference_response = sdk.preference().create(preference_data)
        
        if preference_response["status"] == 201:
            return preference_response["response"]["id"]
        else:
            return None
    except Exception as e:
        print(f"Exceção ao configurar MP: {e}")
        return None

# =========================================================
# Views de Produto e Carrinho (PRODUCT APP)
# =========================================================

def listar_produtos(request):
    """
    Lista todos os produtos (Necessária para a rota '').
    """
    produtos = Product.objects.all() 
    cart_data = get_cart_data(request)
    
    context = {
        'produtos': produtos,
        'carrinho_total': cart_data['subtotal'] 
    }
    return render(request, 'product/listar_produtos.html', context)

# 1. VIEW PARA EXIBIR O CARRINHO (Nome correto para a URL: carrinho_view)
# Em product/views.py (Exemplo da estrutura da view)

# product/views.py

# ... (Mantenha o resto do código inalterado)

# 1. VIEW PARA EXIBIR O CARRINHO (Nome correto para a URL: carrinho_view)
def carrinho_view(request):
    
    # --- Passo 0: Inicializa o carrinho antes de processar o POST ---
    cart_data = get_cart_data(request)
    frete = request.session.get('frete')
    cep_usado = request.session.get('cep_frete')
    
    # LÓGICA DE CALCULAR FRETE:
    if request.method == 'POST':
        cep = request.POST.get('cep')
        
        if cep:
            try:
                # Sua lógica real de cálculo de frete
                frete_calculado = 15.00 # Exemplo: Simula um valor de frete
                
                # ATUALIZA A SESSÃO COM OS NOVOS VALORES DE FRETE E CEP
                request.session['frete'] = frete_calculado
                request.session['cep_frete'] = cep
                request.session.modified = True 

                # Atualiza as variáveis locais para o render
                frete = frete_calculado
                cep_usado = cep

            except Exception as e:
                print(f"Erro ao calcular frete: {e}")
                # Pode adicionar uma mensagem de erro ao usuário aqui
    
    # --- Passo 1: Prepara o Contexto com TODOS os dados necessários ---
    context = {
        'itens': cart_data['itens'],          # ITENS para o loop no template
        'total': cart_data['subtotal_carrinho'], # TOTAL (subtotal dos itens)
        'frete': frete,                       # Frete (agora atualizado se foi POST)
        'cep': cep_usado,                     # CEP (agora atualizado se foi POST)
    }
    return render(request, 'carrinho.html', context)

# ... (Mantenha o resto do código inalterado)

    # 3. Recupera o frete e o CEP para enviar ao template
    frete = request.session.get('frete')
    cep_usado = request.session.get('cep_frete')
    
    # ... (O restante da lógica para montar os itens e o total) ...
    
    context = {
        # ... outros itens
        'frete': frete,
        'cep': cep_usado,
    }
    return render(request, 'carrinho.html', context)

# product/views.py

# ... (Mantenha todas as imports originais)
from product.utils.cart_utils import get_cart_data, add_to_cart 
# ... (Funções de serviço MP e listar_produtos)

# 🔴 REMOVIDO: A função carrinho_view (que estava aqui) foi movida para users/views.py

# 2. VIEW PARA ADICIONAR PRODUTOS (Com debug de Sessão)
def adicionar_produto(request, product_id):
    # --- DEBUG: Verifica ID da Sessão ---
    print(f"--- DEBUG: Sessão (ADICIONAR) ID: {request.session.session_key} ---")
    print(f"--- DEBUG: FUNÇÃO ADICIONAR PRODUTO CHAMADA para ID {product_id} ---")
    
    if add_to_cart(request, product_id):
        print(f"--- DEBUG: add_to_cart retornou True ---") 
        return redirect('carrinho_view')
    
    print(f"--- DEBUG: add_to_cart retornou False ---") 
    return redirect('listar_produtos')

# ... (Mantenha todas as outras views: aumentar_quantidade, diminuir_quantidade, 
# remover_produto, finalizar_pedido, pedido_confirmado_view, etc.)


# 3. VIEW PARA AUMENTAR QUANTIDADE (Corrigida para coincidir com as URLs)
# No arquivo product/views.py

def aumentar_quantidade(request, product_id): # 🔴 CORREÇÃO AQUI
    # Lógica para aumentar a quantidade
    carrinho = request.session.get('carrinho', {})
    product_id_str = str(product_id)

    if product_id_str in carrinho:
        # Aumentar a quantidade (assumindo que é no dicionário 'quantidade')
        carrinho[product_id_str]['quantidade'] += 1 
        
        # Salvar e sinalizar a modificação
        request.session['carrinho'] = carrinho
        request.session.modified = True 
        
    return redirect('carrinho_view')

# *NOTA: Você ainda precisará de 'diminuir_quantidade' e 'remover_produto'. Adicione-as 
# se elas existirem em seu product/urls.py.*

# --- VIEW PRINCIPAL DE CHECKOUT ---
@login_required(login_url='login') 
@transaction.atomic
def finalizar_pedido(request):
    """Converte o carrinho de sessão em Order e cria a preferência MP."""
    # (Corpo da função, como na resposta anterior)
    cart_data = get_cart_data(request)
    carrinho_session = cart_data['carrinho_session']
    
    if not carrinho_session:
        return redirect('carrinho_view')

    user = request.user 

    # 1. CRIAR A ORDEM (Order)
    order = Order.objects.create(
        user=user, 
        total=cart_data['total'],
        shipping_value=cart_data['frete'],
        cep=cart_data['cep'],
        status='Aguardando Pagamento'
    )
    
    itens_mercadopago = []
    
    # 2. CRIAR OS ITENS DO PEDIDO (ItemPedido)
    for item_carrinho in cart_data['itens']:
        product = item_carrinho['produto']
        quantidade = item_carrinho['quantidade']
        subtotal = item_carrinho['subtotal']
        
        ItemPedido.objects.create(
            order=order,
            product=product,
            quantity=quantidade,
            subtotal=subtotal
        )
        
        # 3. PREPARAR ITENS PARA MP
        itens_mercadopago.append({
            "title": product.name,
            "quantity": quantidade,
            "unit_price": float(product.price),
        })

    # 4. INICIAR PAGAMENTO COM MERCADO PAGO
    preference_id = criar_preferencia_mercadopago(order, itens_mercadopago)
    
    if preference_id:
        # 5. Limpar o carrinho
        if 'carrinho' in request.session:
            del request.session['carrinho']
            del request.session['cep']
            del request.session['frete']
            request.session.modified = True
            
        return render(request, 'pagamento.html', {
            'order': order,
            'preference_id': preference_id,
            'settings': {'MP_PUBLIC_KEY': settings.MP_PUBLIC_KEY}
        })
    else:
        # Se falhar, deleta a ordem
        order.delete()
        return redirect('carrinho_view')

# --- VIEWS DE RETORNO DO MERCADO PAGO (PLACEHOLDERS) ---
def pedido_confirmado_view(request, order_id):
    """Lógica para pedido APROVADO pelo Mercado Pago."""
    return render(request, 'product/pedido_confirmado.html', {'order_id': order_id, 'status': 'Aprovado'})

def pedido_pendente_view(request, order_id):
    """Lógica para pedido PENDENTE de pagamento."""
    return render(request, 'product/pedido_pendente.html', {'order_id': order_id, 'status': 'Pendente'})

def pedido_falha_view(request, order_id):
    """Lógica para pedido REJEITADO/FALHADO pelo Mercado Pago."""
    return render(request, 'product/pedido_falha.html', {'order_id': order_id, 'status': 'Falha'})

# --- VIEW DE NOTIFICAÇÃO (WEBHOOK) ---
@csrf_exempt 
def mercadopago_webhook(request):
    # Lógica do webhook aqui
    return JsonResponse({"status": "ok"}, status=200)


# product/views.py (Adicione estas também, se necessário)

# No arquivo product/views.py
from django.shortcuts import redirect

def diminuir_quantidade(request, product_id):
    carrinho = request.session.get('carrinho', {})
    product_id_str = str(product_id)

    if product_id_str in carrinho:
        # Assumindo que o item do carrinho é um dicionário e a quantidade está em 'quantidade'
        
        # 🔴 CORREÇÃO AQUI (Linha 200 ou próxima):
        # Acesse a chave 'quantidade' dentro do dicionário do produto
        carrinho[product_id_str]['quantidade'] -= 1 
        
        # Verifica se a quantidade chegou a zero
        if carrinho[product_id_str]['quantidade'] <= 0:
            del carrinho[product_id_str]
        
        # Salva e sinaliza a modificação
        request.session['carrinho'] = carrinho
        request.session.modified = True 
        
    return redirect('carrinho_view')

# Em product/views.py

from django.shortcuts import redirect

def remover_produto(request, product_id):
    carrinho = request.session.get('carrinho', {})
    
    # Converte a ID para string, pois as chaves do carrinho são strings
    product_id_str = str(product_id)

    # 1. Verifica se o produto existe no carrinho
    if product_id_str in carrinho:
        
        # 2. REMOVE o item do dicionário do carrinho
        del carrinho[product_id_str] 
        
        # 3. ATUALIZA o dicionário da sessão com o dicionário modificado
        request.session['carrinho'] = carrinho
        
        # 4. SINALIZA ao Django que a sessão foi alterada (CRUCIAL!)
        request.session.modified = True 
        
    return redirect('carrinho_view') # Redireciona para atualizar a página