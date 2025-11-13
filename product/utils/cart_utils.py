# product/utils/cart_utils.py

from product.models import Product
from decimal import Decimal

# =========================================================
# FUNÇÃO PARA ADICIONAR/SALVAR NA SESSÃO
# =========================================================
def add_to_cart(request, product_id):
    try:
        carrinho = request.session.get('carrinho', {})
        product_id_str = str(product_id)
        
        # 1. Lógica de adição
        if product_id_str in carrinho:
            carrinho[product_id_str]['quantidade'] += 1
        else:
            product = Product.objects.get(id_product=product_id)
            carrinho[product_id_str] = {
                'produto_id': product_id,
                'nome': product.name,
                # Salvar como string é CRUCIAL para serialização da sessão
                'preco': str(product.price), 
                'quantidade': 1,
            }

        # 2. CRÍTICO: Sobrescreve e salva a sessão
        request.session['carrinho'] = carrinho 
        request.session.modified = True 
        print(f"DEBUG CARRINHO SALVO: {request.session.get('carrinho')}")
        return True 
    
    except Product.DoesNotExist:
        print(f"DEBUG: Produto ID {product_id} não encontrado.")
        return False
    except Exception as e:
        print(f"ERRO FATAL (Cart Utils - Add): {e}")
        return False

# =========================================================
# FUNÇÃO PARA LER/PROCESSAR OS DADOS DO CARRINHO
# =========================================================
# users/views.py (ou utils.py, onde estiver a get_cart_data)

def get_cart_data(request):
    # 1. Tenta obter o carrinho da sessão
    cart = request.session.get('carrinho', {})
    
    itens = []
    total_acumulado = 0.0  # Mude para float para garantir precisão
    
    # Itera sobre os IDs dos produtos no carrinho
    for produto_id, dados in cart.items():
        
        # --- CORREÇÃO DE TIPO DE DADO AQUI ---
        # Garantindo que preco e quantidade sejam números antes de usar
        try:
            # Preço deve ser float (tem casas decimais)
            preco = float(dados['preco'])
            # Quantidade deve ser int (se não usa meias quantidades)
            quantidade = int(dados['quantidade']) 
        except (ValueError, TypeError):
            # Se o valor for inválido na sessão, pula o item ou trata como zero
            preco = 0.0
            quantidade = 0
        # ------------------------------------
        
        # Lógica para calcular o subtotal da linha
        subtotal_item = preco * quantidade 
        
        # 2. SOMA O SUBTOTAL DE CADA ITEM AO TOTAL ACUMULADO
        total_acumulado += subtotal_item  
        
        # Adiciona o item formatado à lista 'itens'
        itens.append({
            'produto': { 
                # O template espera 'name', mas o dado da sessão é 'nome'. Fazemos a conversão aqui.
                'name': dados['nome'],
                'id': produto_id, # <-- CORREÇÃO: Mude a chave de saída para 'name'
            },
            'quantidade': quantidade, # Corrigido para a variável int
            'subtotal_item': subtotal_item, 
        })
        
    return {
        'itens': itens,
        'subtotal': total_acumulado  # 3. RETORNA O VALOR TOTAL ACUMULADO
    }