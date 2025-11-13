from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name

from django.db import models

# O modelo Users mapeia para a tabela 'users' do seu banco de dados
class Users(models.Model):
    id_users = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    birth = models.CharField(max_length=8) # Recomendado usar DateField ou CharField, dependendo do formato
    cpf = models.IntegerField() # Cuidado: CPF deve ser CharField ou BigIntegerField no Django, pois int(11) no MySQL não suporta todos os CPFs
    telephone = models.IntegerField() # Recomendado usar CharField
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=30)
    
    # Se você estiver usando o sistema de autenticação do Django, 
    # este modelo deve ser configurado como AUTH_USER_MODEL no settings.py 
    # e deve ser uma subclasse de AbstractBaseUser.
    
    class Meta:
        managed = False # Indica que a tabela 'users' já existe no DB
        db_table = 'users'

    def __str__(self):
        return self.name

# Adicione outros modelos do app_admin abaixo, se houver.