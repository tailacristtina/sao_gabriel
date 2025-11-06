from django.db import models

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

from users.models import Users

class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Users, on_delete=models.CASCADE)
    data = models.DateTimeField(auto_now_add=True)
    total = models.FloatField()
    status = models.CharField(max_length=20, default='Pendente')

    class Meta:
        db_table = 'pedido'

    def __str__(self):
        return f"Pedido {self.id_pedido} - {self.usuario.name}"


class ItemPedido(models.Model):
    id_item = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    produto = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    subtotal = models.FloatField()

    class Meta:
        db_table = 'item_pedido'

    def __str__(self):
        return f"{self.quantidade}x {self.produto.name}"
