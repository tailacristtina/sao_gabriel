# payment/urls.py

from django.urls import path
from . import views

app_name = 'payment' 

urlpatterns = [
    # 1. Inicia o processo de Checkout Pro
    path('iniciar/', views.iniciar_pagamento_view, name='iniciar_pagamento'), 
    
    # 2. Recebe as notificações de Webhook do Mercado Pago
    path('webhook/', views.mp_webhook_view, name='mp_webhook'), 
]