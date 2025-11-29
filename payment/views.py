# payment/views.py

from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Importe o serviço
from .services import create_mp_preference 

# Importe seu modelo de Pedido do app 'store'
# from store.models import Order # Substitua pelo nome correto do seu modelo

# --- Ação 1: Disparar o Checkout Pro ---
def iniciar_pagamento_view(request):
    """
    Recebe o ID do Pedido e chama o serviço do Mercado Pago.
    """
    order_id = request.GET.get('order_id')
    
    if not order_id:
        messages.error(request, "ID do pedido não fornecido.")
        # Ajuste o reverse para a sua rota de carrinho correta
        return redirect(reverse('store:carrinho')) 
    
    try:
        # 1. Recupera o pedido do banco de dados
        # pedido = Order.objects.get(id_order=order_id)
        # SIMULAÇÃO: 
        class MockOrder:
             id_order = order_id
             total = Decimal(request.session.get('total_pedido', '100.00')) # Use o total salvo
             user = request.user # Assumindo que o usuário está logado
        pedido = MockOrder() 

    except Exception: # Troque para 'Order.DoesNotExist'
        messages.error(request, f"Pedido {order_id} não encontrado.")
        return redirect(reverse('store:carrinho'))

    # 2. Chama o serviço de pagamento
    mp_data = create_mp_preference(pedido, request)
    
    # 3. Redireciona
    if mp_data and mp_data.get('init_point'):
        return redirect(mp_data['init_point'])
    else:
        messages.error(request, 'Erro ao comunicar com o Mercado Pago. Tente novamente.')
        return redirect(reverse('store:carrinho'))


# --- Ação 2: Webhook do Mercado Pago (CRÍTICO) ---
@csrf_exempt
def mp_webhook_view(request):
    """
    Recebe as notificações de status de pagamento do Mercado Pago (IPN).
    """
    if request.method == 'POST':
        # O MP manda os dados via GET ou POST dependendo do tipo de notificação
        topic = request.GET.get('topic', request.POST.get('topic'))
        resource_id = request.GET.get('id', request.POST.get('id')) 

        if topic and resource_id:
            # 1. Chamar um serviço para processar a notificação
            # service.process_webhook(topic, resource_id) 
            
            # **LÓGICA CRÍTICA DE ATUALIZAÇÃO DO PEDIDO**
            # Se for 'payment' ou 'merchant_order', você deve buscar o status real
            # no MP e atualizar o status do Pedido no seu DB (Aprovado, Recusado, etc.).
            
            # Retorno obrigatório para o MP saber que você recebeu a notificação
            return HttpResponse(status=200) 
        
    return HttpResponse(status=400) # Requisição inválida