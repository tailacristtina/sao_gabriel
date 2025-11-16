import mercadopago
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from decimal import Decimal
from django.contrib import messages

from product.utils.cart_utils import get_cart_data 
# Importe seus modelos de Pedido e ItemPedido, se necessário
# from store.models import Pedido, ItemPedido 

# --- FUNÇÃO 1: INICIAR O CHECKOUT DO MERCADO PAGO ---
def iniciar_pagamento_view(request):
    
    # CRÍTICO: 1. Captura o order_id enviado da finalizar_pedido_view
    order_id = request.GET.get('order_id')
    
    if not order_id:
        messages.error(request, "ID do pedido não fornecido.")
        return redirect(reverse('users:carrinho')) 
    
    # LÓGICA DE RECUPERAÇÃO DO PEDIDO (DESCOMENTAR E IMPLEMENTAR)
    # try:
    #     pedido = Pedido.objects.get(id=order_id)
    # except Pedido.DoesNotExist:
    #     messages.error(request, f"Pedido {order_id} não encontrado.")
    #     return redirect(reverse('users:carrinho')) 

    # SIMULAÇÃO: Use os dados da sessão/mock se ainda não tiver a lógica do DB
    cart_data = get_cart_data(request) 
    itens = cart_data.get('itens', [])
    
    # Para simular o total do pedido já que o carrinho foi limpo no POST anterior
    total_pedido = Decimal(request.session.get('total_pedido', cart_data.get('subtotal', Decimal('0.00')))) 
    frete_valor = Decimal(request.session.get('frete', '0.00'))
    total_compra = total_pedido + frete_valor
    

    if not itens and total_compra <= 0:
        messages.warning(request, "Não há itens ou valor no pedido para pagar.")
        return redirect(reverse('users:carrinho')) 
    
    # 2. Configurar o SDK
    try:
        mp = mercadopago.SDK(settings.MP_ACCESS_TOKEN) 
    except AttributeError:
        messages.error(request, 'Erro: MP_ACCESS_TOKEN não configurado no settings.py.')
        return render(request, 'erro_pagamento.html', {'message': 'Erro de configuração do Mercado Pago.'})
    
    # 3. Preparar os itens (aqui seria melhor usar os OrderItems reais do DB)
    items_mp = []
    # USANDO O TOTAL SIMULADO DO PEDIDO PARA FACILITAR:
    items_mp.append({
        "title": f"Compra São Gabriel Pedido #{order_id}",
        "quantity": 1,
        "unit_price": float(total_compra), 
    })
        
    preference_data = {
        "items": items_mp,
        # CRÍTICO: Usar o ID do pedido real como referência externa
        "external_reference": order_id, 
        "back_urls": {
            # CRÍTICO: Aponta para a view de confirmação no app 'users'
            "success": request.build_absolute_uri(reverse('users:pedido_confirmado') + f'?order_id={order_id}'),
            "failure": request.build_absolute_uri(reverse('users:pedido_confirmado') + f'?order_id={order_id}'),
            "pending": request.build_absolute_uri(reverse('users:pedido_confirmado') + f'?order_id={order_id}'),
        },
        "auto_return": "all", # Redireciona automaticamente
        "payer": {
            "email": request.session.get('user_email', 'anonimo@site.com'), # Tente pegar o email do user logado
        }
    }
    
    preference = mp.preference().create(preference_data)

    # 4. Redirecionar
    if preference and preference.get('response', {}).get('init_point'):
        return redirect(preference['response']['init_point'])
    else:
        error_message = preference.get('status_detail') if preference and preference.get('status_detail') else 'Erro desconhecido ao criar preferência de pagamento.'
        messages.error(request, f'Erro MP: {error_message}')
        return redirect(reverse('users:carrinho'))

# --- FUNÇÃO 2: RECEBER O FEEDBACK DO MERCADO PAGO ---
# DEVE SER REMOVIDA SE VOCÊ USAR APENAS users:pedido_confirmado
def mp_feedback_view(request):
    messages.info(request, "Feedback do MP recebido, mas o fluxo principal é users:pedido_confirmado.")
    # Implemente a lógica necessária se esta view for mantida no seu urls.py
    # Por enquanto, redireciona ou renderiza algo simples
    return redirect(reverse('index'))