from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.urls import reverse
from django.contrib import messages
from decimal import Decimal

from users.models import Users
from .models import Order, ItemPedido 
from product.models import Product 
from store.utils.cart_utils import get_cart_data, add_to_cart 
from payment.services import create_mp_preference 

# =========================================================
# VIEWS GERAIS E DE CARRINHO
# =========================================================

def index_home(request):
    context = {} 
    return render(request, 'index.html', context)

def carrinho_view(request):
    cart_data = get_cart_data(request)
    frete_session = request.session.get('frete') 
    
    frete = Decimal(frete_session) if frete_session else Decimal('0.00')
    total_compra = cart_data['subtotal'] + frete

    context = {
        'itens': cart_data['itens'], 
        'subtotal': cart_data['subtotal'], 
        'frete': frete, 
        'total_compra': total_compra
    }
    return render(request, 'carrinho.html', context)


def adicionar_produto(request, product_id):
    if add_to_cart(request, product_id):
        return redirect(reverse('store:carrinho')) 
    messages.error(request, "Produto não encontrado ou erro ao adicionar.")
    return redirect(reverse('product:listar_produtos')) 


def aumentar_quantidade(request, product_id):
    carrinho = request.session.get('carrinho', {})
    product_id_str = str(product_id)
    if product_id_str in carrinho:
        carrinho[product_id_str]['quantidade'] += 1 
        request.session['carrinho'] = carrinho
        request.session.modified = True 
    return redirect(reverse('store:carrinho'))


def diminuir_quantidade(request, product_id):
    carrinho = request.session.get('carrinho', {})
    product_id_str = str(product_id)
    if product_id_str in carrinho:
        carrinho[product_id_str]['quantidade'] -= 1 
        if carrinho[product_id_str]['quantidade'] <= 0:
            del carrinho[product_id_str]
        request.session['carrinho'] = carrinho
        request.session.modified = True 
    return redirect(reverse('store:carrinho'))


def remover_produto(request, product_id):
    carrinho = request.session.get('carrinho', {})
    product_id_str = str(product_id)
    if product_id_str in carrinho:
        del carrinho[product_id_str] 
        request.session['carrinho'] = carrinho
        request.session.modified = True 
    return redirect(reverse('store:carrinho'))


# ---------------------------------------------------------
# VIEW PRINCIPAL DE CHECKOUT (CORREÇÃO FINAL DO BLOCO ATÔMICO)
# ---------------------------------------------------------
@transaction.non_atomic_requests
def finalizar_pedido_view(request):
    user_id = request.session.get('user_id')
    
    # 1. Checagem de autenticação e obtenção do objeto User
    try:
        if not user_id:
            messages.error(request, "Você precisa estar logado para finalizar o pedido.")
            return redirect('users:login')
        user = Users.objects.get(pk=user_id) 
    except Users.DoesNotExist:
        messages.error(request, "Sessão inválida. Faça login novamente.")
        request.session.flush() 
        return redirect('users:login')
        
    # 2. Obtenção dos dados do carrinho
    cart_data = get_cart_data(request)
    itens = cart_data.get('itens', [])
    subtotal = cart_data.get('subtotal', Decimal('0.00'))
    frete_valor = Decimal(request.session.get('frete', '0.00'))
    total_compra = subtotal + frete_valor
    
    if not itens:
        messages.warning(request, "Seu carrinho está vazio.")
        return redirect(reverse('store:carrinho'))

    if request.method == 'POST':
        # 3. Captura dados do formulário
        cep = request.POST.get('cep')
        endereco = request.POST.get('endereco')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')

        if not all([cep, endereco, cidade, estado]):
            messages.error(request, "Todos os campos de endereço são obrigatórios.")
            return redirect(reverse('store:finalizar_pedido'))
        
        # Variáveis inicializadas
        order = None
        order_items_list = []
        
        order = None
        order_items_list = []

        try:
            # 1. CRIAÇÃO FORÇADA DA ORDER (FORA DO ATOMIC PARA OBTER O ID IMEDIATAMENTE)
            # Isso resolve o problema de 'order_id cannot be null' no MySQL.
            order = Order.objects.create(
                user=user, 
                total=total_compra,
                shipping_value=frete_valor,
                cep=cep,
                address=endereco,
                city=cidade,
                state=estado,
                status='Pendente Pagamento'
            )
            order = Order.objects.filter(user=user).latest('created_at')
            # O atomic agora protege apenas a criação de ItemPedido (usando o ID já gerado)
            with transaction.atomic():
                
                # 5. CRIA OS ITENS DO PEDIDO (O order.id_order agora é um valor CONHECIDO)
                for item_carrinho in itens:
                    produto_id = item_carrinho.get('produto_id')
                    produto_obj = item_carrinho.get('produto')
                    
                    if not produto_obj:
                        try:
                            produto_obj = Product.objects.get(id_product=produto_id)
                        except Product.DoesNotExist:
                            # Se falhar aqui, o atomic fará o rollback de todos os itens, 
                            # mas a Order principal (criada fora) permanece como rascunho.
                            raise Exception(f"Produto inválido no carrinho (ID: {produto_id})")

                    item_pedido_obj = ItemPedido.objects.create(
                        order_id=order.id_order, # ✅ AGORA O ID ESTÁ GARANTIDO
                        product=produto_obj, 
                        quantity=item_carrinho['quantidade'],
                        unit_price=item_carrinho['preco_unitario'],
                        subtotal=item_carrinho['subtotal_item']
                    )
                    order_items_list.append(item_pedido_obj)
                    
            # FIM DO transaction.atomic()
                    
            # 3. CHAMA API EXTERNA (FORA DA TRANSAÇÃO)
            mp_data = create_mp_preference(order, request, order_items_list)
                            
            if mp_data and mp_data.get('init_point'):
                # 4. SALVAMENTO FINAL SEGURO
                order.mp_preference_id = mp_data['id']
                order.save(update_fields=['mp_preference_id'])
                
                # Limpa o carrinho
                if 'carrinho' in request.session:
                    del request.session['carrinho']
                    request.session.modified = True

                return redirect(mp_data['init_point'])
            else:
                # Se o MP falhar, a Order e os Itens estão salvos no DB.
                messages.error(request, "Falha na integração com o Mercado Pago. Tente novamente.")
                return redirect(reverse('store:carrinho')) 
                
        except Exception as e:
            import traceback
            print("-" * 50)
            print("ERRO DE RASTREAMENTO COMPLETO FINAL:")
            traceback.print_exc()
            print("-" * 50)
            
            messages.error(request, f"Ocorreu um erro crítico ao finalizar a compra. Tente novamente.")
            return redirect(reverse('store:carrinho'))
        
    # GET: renderiza formulário de endereço
    context = {
        'total_compra': total_compra,
        'itens_carrinho': itens,
        'frete': frete_valor,
        'subtotal': subtotal,
        'user': user,
    }
    return render(request, 'finalizar_pedido.html', context)


# ---------------------------------------------------------
# VIEWS DE FEEDBACK PÓS-PAGAMENTO
# ---------------------------------------------------------
def pedido_confirmado_view(request):
    """
    Trata o retorno do usuário após tentar pagar no Mercado Pago (success/pending/failure).
    """
    order_id = request.GET.get('order_id')
    
    try:
        order = Order.objects.get(id_order=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Pedido não encontrado.")
        return redirect(reverse('product:listar_produtos'))

    context = {
        'order': order,
        'status_mensagem': f"Seu pedido #{order_id} está com status: {order.status}. Você será notificado sobre a confirmação final."
    }
    
    return render(request, 'pedido_confirmado.html', context)