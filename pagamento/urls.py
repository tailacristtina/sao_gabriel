from django.urls import path
from . import views

# O namespace 'pagamento' é opcional, mas ajuda a evitar colisões de nomes
app_name = 'pagamento' 

urlpatterns = [
    # URL completa será: /checkout/iniciar/
    path('iniciar/', views.iniciar_pagamento_view, name='iniciar_pagamento'), 
    
    # URL completa será: /checkout/feedback/ (Para onde o Mercado Pago retorna)
    path('feedback/', views.mp_feedback_view, name='mp_feedback'),
]