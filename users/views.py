from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from decimal import Decimal

# Importações obrigatórias
from .models import Users 
from .forms import RegisterForm, LoginForm 
from product.utils.cart_utils import get_cart_data 

# IMPORTANTE: Você precisa adicionar os imports dos seus modelos de Pedido (Order) aqui!
# Exemplo (ajuste o caminho de importação se necessário):
# from order.models import Order, OrderItem 


# =========================================================
# VISTAS DE AUTENTICAÇÃO E PERFIL
# =========================================================

def perfil_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.info(request, "Faça login para acessar o perfil.")
        return redirect('login')

    user = Users.objects.get(id_users=user_id)
    return render(request, 'users/perfil.html', {'user': user})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect('index')
        else:
            messages.error(request, "Erro no cadastro. Verifique os dados e tente novamente.")
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.session.get('user_id'):
        return redirect('index') 
        
    if request.method == 'POST':
        email = request.POST.get('email', '').strip() 
        password = request.POST.get('password', '').strip() 

        try:
            user = Users.objects.get(email=email)

            if check_password(password, user.password):
                request.session['user_id'] = user.id_users
                request.session['user_name'] = user.name

                messages.success(request, f"Bem-vindo(a), {user.name}!")

                if user.id_users == 1:
                    return redirect('/app_admin/dashboard/')
                else:
                    return redirect('index')

            else:
                messages.error(request, "Email ou senha incorretos.")

        except Users.DoesNotExist:
            messages.error(request, "Email ou senha incorretos.")

    return render(request, 'users/login.html')

def logout_view(request):
    request.session.flush()
    messages.info(request, "Você saiu da sua conta.")
    return redirect('login')


def home_view(request):
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    return render(request, 'index.html', {'user_id': user_id, 'user_name': user_name})

# =========================================================
# Lógica do Carrinho
# =========================================================
def carrinho_view(request):
    cart_data = get_cart_data(request)
    frete_session = request.session.get('frete') 
    cep_usado = request.session.get('cep_frete')
    
    frete = None
    if frete_session:
        try:
            frete = Decimal(frete_session)
        except:
            pass
    
    # LÓGICA DE CALCULAR FRETE:
    if request.method == 'POST':
        cep = request.POST.get('cep')
        
        if cep:
            try:
                # Sua lógica real de cálculo de frete
                frete_calculado = Decimal('15.00') # Exemplo
                
                # ATUALIZA A SESSÃO com o frete como string
                request.session['frete'] = str(frete_calculado) 
                request.session['cep_frete'] = cep
                request.session.modified = True 

                # Atualiza as variáveis locais para o render
                frete = frete_calculado
                cep_usado = cep

            except Exception as e:
                print(f"Erro ao calcular frete: {e}")
    
    context = {
        'itens': cart_data['itens'],            
        'subtotal': cart_data['subtotal'], 
        'frete': frete,                      
        'cep': cep_usado,                      
    }
    
    return render(request, 'carrinho.html', context)


# =========================================================
# Lógica de Finalizar Pedido (Checkout)
# =========================================================
def finalizar_pedido_view(request):
    # 1. Verifica se o usuário está logado
    if 'user_id' not in request.session:
        messages.error(request, "Faça login para finalizar o pedido.")
        return redirect(reverse('login'))

    # 2. Recupera os dados do carrinho
    cart_data = get_cart_data(request)
    itens = cart_data.get('itens', [])
    subtotal = cart_data.get('subtotal', Decimal('0.00'))
    user_id = request.session['user_id']
    
    # Se o carrinho estiver vazio, redireciona de volta
    if not itens:
        messages.warning(request, "Seu carrinho está vazio.")
        return redirect(reverse('carrinho'))

    # 3. Processamento do Formulário de Endereço (Método POST)
    if request.method == 'POST':
        # Captura todos os dados do formulário de endereço de finalizar_pedido.html
        cep = request.POST.get('cep')
        endereco = request.POST.get('endereco')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')

        # 1. Obter o objeto User
        try:
            user = Users.objects.get(id_users=user_id)
        except Users.DoesNotExist:
            messages.error(request, "Usuário não encontrado.")
            return redirect(reverse('carrinho'))

        # 2. Validar endereço básico
        if not all([cep, endereco, cidade, estado]):
            messages.error(request, "Todos os campos de endereço são obrigatórios.")
            return redirect(reverse('users:finalizar_pedido'))

        # === LÓGICA CRÍTICA: CRIAÇÃO E SALVAMENTO DO PEDIDO NO BANCO DE DADOS ===
        try:
            # 3. Criar o objeto Order (Pedido)
            # order = Order.objects.create(
            #     user=user,
            #     total=subtotal + Decimal(request.session.get('frete', '0.00')), # Subtotal + Frete
            #     shipping_value=Decimal(request.session.get('frete', '0.00')),
            #     shipping_address=f"CEP: {cep}, {endereco}, {cidade} - {estado}",
            #     status='PENDING_PAYMENT' 
            # )
            
            # --- SIMULAÇÃO: Use um ID real do objeto Order criado
            order_id = 999 
            # O ID real seria: order_id = order.id 
            messages.info(request, f"Pedido {order_id} registrado temporariamente.")

            # 4. Criar os objetos OrderItem (Itens do Pedido)
            # for item in itens:
            #     OrderItem.objects.create(
            #         order=order,
            #         product=item['produto'], 
            #         quantity=item['quantidade'],
            #         price=item['subtotal_item']
            #     )

            # 5. Limpa o carrinho da sessão após a criação bem-sucedida
            if 'carrinho' in request.session:
                # O carrinho só deve ser limpo AQUI se o pagamento for garantido ou mockado.
                # Para evitar perda de dados, vamos MOCKAR a limpeza e confiar no retorno do MP.
                # request.session['carrinho'] = {}
                # request.session.modified = True
                pass
            
            # Salvamos o total na sessão temporariamente para o caso de o carrinho ter sido limpo
            request.session['total_pedido'] = str(subtotal)
            
            # 6. Redirecionamento para o Pagamento, passando o ID do pedido
            messages.success(request, "Pedido criado com sucesso! Redirecionando para o pagamento.")
            # É CRÍTICO passar o order_id para a view de pagamento
            return redirect(reverse('pagamento:iniciar_pagamento') + f'?order_id={order_id}') 
            
        except Exception as e:
            # Tratar erros de banco de dados
            messages.error(request, f"Erro ao criar o pedido: {e}")
            return redirect(reverse('carrinho')) 
    
    # 7. Renderização Inicial (Método GET) - Mostra o formulário de endereço
    context = {
        'total': subtotal,
        'produtos': itens, 
        'itens_carrinho': itens,
        'cep_frete': request.session.get('cep_frete', '')
    }

    return render(request, 'finalizar_pedido.html', context)


# =========================================================
# Lógica de Confirmação (Retorno do Mercado Pago)
# =========================================================
def pedido_confirmado_view(request):
    # Esta view deve ser a URL de RETORNO (Success URL) configurada no Mercado Pago.
    
    # Exemplo de como pegar o ID do pedido da URL (passado pelo Mercado Pago/iniciar_pagamento)
    order_id = request.GET.get('order_id') 
    
    # LÓGICA DE ATUALIZAÇÃO DO STATUS:
    
    # Simulação: Recuperação e atualização de status
    # status_mp = request.GET.get('status') # status do MP: approved, pending, failure
    
    # 1. Busca o pedido: 
    # try:
    #     order = Order.objects.get(id=order_id)
    # except Order.DoesNotExist:
    #     messages.error(request, "Pedido não encontrado para confirmação.")
    #     return redirect(reverse('index'))
    
    # 2. Atualiza o status (apenas se for aprovado no retorno provisório)
    # if status_mp == 'approved' and order.status != 'PAID':
    #     order.status = 'PAID'
    #     order.save()
        
    # 3. Limpar o carrinho (caso não tenha sido limpo antes)
    if 'carrinho' in request.session:
        request.session['carrinho'] = {}
        request.session.modified = True

    # SIMULAÇÃO de dados para renderizar o template
    # Estes dados devem vir do objeto Order real
    order_data = {
        'user': {'name': request.session.get('user_name', 'Cliente')},
        'id_order': order_id or 'N/A',
        'total': '150.00', 
        'shipping_value': '15.00',
        'status': 'Pago (Confirmado)',
        'created_at': '2025-11-13T17:30:00Z' 
    }
    
    messages.success(request, f"O status do seu pedido #{order_id} foi atualizado.")
    return render(request, 'pedido_confirmado.html', {'order': order_data})