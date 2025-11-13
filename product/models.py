from django.db import models
from app_admin.models import Users 

# --- Modelos Auxiliares (Baseado no seu BD) ---
# Adicione um modelo para a tabela 'Store' se você ainda não o tem,
# pois 'store_product' se relaciona com ela.
class Store(models.Model):
    id_store = models.AutoField(primary_key=True)
    fk_users_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    qt_product = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'store'

# --- Modelo Product (Sem alterações) ---
class Product(models.Model):
    id_product = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    price = models.FloatField()
    fk_category_id = models.IntegerField()

    class Meta:
        managed = False 
        db_table = 'product'

    def __str__(self):
        return self.name

# --- Modelo Order (O registro final do pedido) ---
# Este modelo permanece para salvar o registro final de compra.
class Order(models.Model):
    id_order = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE) 
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pendente')
    shipping_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cep = models.CharField(max_length=9, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)

    class Meta:
        db_table = 'order'

    def __str__(self):
        return f"Pedido #{self.id_order} - {self.user.name}"


# --- Modelo ItemPedido (Mapeado para a tabela store_product) ---
# Usamos o nome 'ItemPedido' para clareza no código Django
# e mapeamos para a tabela 'store_product' no banco de dados.
class ItemPedido(models.Model):
    # Relacionamento com Order (supondo que Order salva o ID do carrinho/Store)
    # NOTA: Se 'store_product' é o seu carrinho, ele se relaciona com 'Store', não 'Order'.
    # Para o checkout, criamos uma nova tabela 'ItemPedido' relacionada a 'Order'.
    # Mantemos o modelo ItemPedido original, mas *corrigimos a lógica de checkout* # para USAR a tabela 'Order' e 'ItemPedido' que é criada.
    order = models.ForeignKey(Order, on_delete=models.CASCADE) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1) # Renomeamos 'amound' para 'quantity'
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        # AQUI VAI O NOME DA TABELA QUE SERÁ CRIADA/USADA PELO DJANGO
        db_table = 'item_pedido' 

    def __str__(self):
        return f'{self.quantity}x {self.product.name}'