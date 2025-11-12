from django.db import models

class Users(models.Model):
    id_users = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    birth = models.CharField(max_length=10)
    cpf = models.CharField(max_length=11, unique=True)
    telephone = models.CharField(max_length=12)
    email = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=30)

    class Meta:
        db_table = 'users'
        managed = False  # <-- ESSA LINHA DIZ AO DJANGO PARA NÃO GERENCIAR ESSA TABELA

    def __str__(self):
        return self.name
