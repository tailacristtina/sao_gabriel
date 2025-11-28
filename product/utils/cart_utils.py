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

        # Se já existir, só incrementa
        if product_id_str in carrinho and isinstance(carrinho[product_id_str], dict):
            carrinho[product_id_str]['quantidade'] += 1
        else:
            # Carrega o produto do banco
            product = Product.objects.get(id_product=product_id)

            # Armazena como dicionário (muito importante!)
            carrinho[product_id_str] = {
                'produto_id': product_id,
                'nome': product.name,
                'preco': str(product.price),  # string para sessão
                'quantidade': 1,
            }

        # Salva a sessão
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
def get_cart_data(request):
    cart = request.session.get('carrinho', {})

    itens = []
    total_acumulado = 0.0

    for produto_id, dados in cart.items():

        # 🔴 PROTEÇÃO CONTRA DADOS INVÁLIDOS
        if not isinstance(dados, dict):
            print(f"ITEM INVÁLIDO NA SESSÃO: {produto_id} → {dados}")
            continue

        # Garantir tipos corretos
        try:
            preco = float(dados.get('preco', 0))
            quantidade = int(dados.get('quantidade', 0))
        except (ValueError, TypeError):
            preco = 0.0
            quantidade = 0

        subtotal_item = preco * quantidade
        total_acumulado += subtotal_item

        itens.append({
            'produto': {
                'name': dados.get('nome', 'Sem nome'),
                'id': produto_id,
            },
            'quantidade': quantidade,
            'subtotal_item': subtotal_item,
        })

    return {
        'itens': itens,
        'subtotal': total_acumulado,
    }
