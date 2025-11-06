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
