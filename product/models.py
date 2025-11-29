# product/models.py

from django.db import models
from app_admin.models import Users # Ajuste este import se Users estiver em outro lugar

# --- Modelo Product (O Plano de Assinatura de Café) ---
class Product(models.Model):
    id_product = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    # Recomendação: Use DecimalField para preços, mas mantive FloatField se for o tipo original do seu DB
    price = models.FloatField() 
    fk_category_id = models.IntegerField()
    # Adicione outros campos como imagem, peso, etc.

    class Meta:
        # 'managed = False' indica que a tabela existe no seu DB e não deve ser criada pelo Django
        managed = False 
        db_table = 'product'

    def __str__(self):
        return self.name

# --- Modelo Auxiliar (Se usado no seu DB para Store/Estoque) ---
# Se este modelo não for usado ativamente no checkout, ele pode permanecer aqui.
class Store(models.Model):
    id_store = models.AutoField(primary_key=True)
    fk_users_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    qt_product = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'store'