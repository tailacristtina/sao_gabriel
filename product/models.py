from django.db import models
from users.models import Users

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

from django.db import models
from users.models import Users

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


class ItemPedido(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity}x {self.product.name}'
