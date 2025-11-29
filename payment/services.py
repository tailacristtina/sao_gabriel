# payment/services.py - CORRIGIDO

import mercadopago
from django.conf import settings
from django.urls import reverse
from decimal import Decimal

# Inicializa o SDK
try:
    MP_SDK = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
except AttributeError:
    # Use um token de placeholder se o settings.MP_ACCESS_TOKEN não existir,
    # apenas para evitar que o SDK quebre no init, mas o retorno será None.
    MP_SDK = None 

# A função AGORA USA order_items_list
def create_mp_preference(order, request, order_items_list):
    """
    Cria a Preferência de Pagamento no Mercado Pago a partir de um objeto Order.
    Usa order_items_list para evitar conflito de transação atômica.
    """
    if not MP_SDK:
        return None

    # Verifica se a lista de itens foi passada e não está vazia
    if not order_items_list:
        print("ERRO: order_items_list está vazia.")
        return None
        
    total_compra = float(order.total)
    
    items_mp = []
    # ESTE DEVE SER O LOOP CORRETO:
    for item in order_items_list: 
        items_mp.append({
            "title": item.product.name,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price), 
        })
         
   
    # URL de Notificação (Webhook) - CRÍTICO!
    notification_url = request.build_absolute_uri(reverse('payment:mp_webhook')) 
    base_url = "http://127.0.0.1:8000"
    pedido_confirmado_path = reverse('store:pedido_confirmado').lstrip('/')

    preference_data = {
        "items": items_mp,
        "external_reference": str(order.id_order), 
        
        # ✅ CORREÇÃO 1: Garanta que o endpoint de sucesso seja válido
        "back_urls": {
            "success": base_url + "/" + pedido_confirmado_path,
            "pending": base_url + "/" + pedido_confirmado_path,
            "failure": base_url + "/" + pedido_confirmado_path,
        },
        
        # ✅ CORREÇÃO 2: Use "all" se desejar retornar sempre.
       # "auto_return": "all", 
       # "notification_url": notification_url, 
        "payer": {
            "email": order.user.email,
        }
    }
    
    preference = MP_SDK.preference().create(preference_data)

    if preference and preference.get('response', {}).get('init_point'):
        return {
            "id": preference['response']['id'],
            "init_point": preference['response']['init_point']
        }
    else:
        # Se você precisar do detalhe do erro do MP
        error_details = preference.get('response', {}).get('message') 
        print(f"Erro ao criar preferência no Mercado Pago: {error_details}")
        return None