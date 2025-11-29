# store/utils/cart_utils.py

from product.models import Product
from decimal import Decimal

# =========================================================
# FUNÇÃO PARA ADICIONAR/SALVAR NA SESSÃO
# =========================================================
def add_to_cart(request, product_id):
    # Sua função de adição (inalterada)
    try:
        carrinho = request.session.get('carrinho', {})
        product_id_str = str(product_id)
        
        if product_id_str in carrinho:
            carrinho[product_id_str]['quantidade'] += 1
        else:
            product = Product.objects.get(id_product=product_id)
            carrinho[product_id_str] = {
                'produto_id': product_id,
                'nome': product.name,
                'preco': str(product.price), # CRÍTICO: Salvar como string
                'quantidade': 1,
            }

        request.session['carrinho'] = carrinho 
        request.session.modified = True 
        return True 
    
    except Product.DoesNotExist:
        return False
    except Exception as e:
        print(f"ERRO FATAL (Cart Utils - Add): {e}")
        return False

# =========================================================
# FUNÇÃO PARA LER/PROCESSAR OS DADOS DO CARRINHO
# =========================================================
def get_cart_data(request):
    cart = request.session.get('carrinho', {})
    
    itens = []
    total_acumulado = Decimal('0.00') 
    
    for produto_id, dados in cart.items():
        try:
            # Usar Decimal para cálculos de moeda é mais seguro que float
            preco = Decimal(dados.get('preco', '0.00')) 
            quantidade = int(dados.get('quantidade', 0)) 
        except (ValueError, TypeError):
            preco = Decimal('0.00')
            quantidade = 0
            
        subtotal_item = preco * quantidade 
        total_acumulado += subtotal_item 
        
        # Recupera o objeto Product real
        try:
             produto_obj = Product.objects.get(id_product=produto_id)
        except Product.DoesNotExist:
             produto_obj = None

        itens.append({
            'produto': produto_obj, # Passar o objeto real é melhor
            'produto_id': int(produto_id),
            'quantidade': quantidade, 
            'subtotal_item': subtotal_item, 
            'preco_unitario': preco
        })
        
    return {
        'itens': itens,
        'subtotal': total_acumulado,
        'carrinho_session': cart # Retorna o dicionário bruto da sessão
    }