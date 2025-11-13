# users/models.py
from django.db import models

class Users(models.Model):
    id_users = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    birth = models.CharField(max_length=10)  
    cpf = models.CharField(max_length=11, unique=True)
    telephone = models.CharField(max_length=12)
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=256, default='!')

    # PROPRIEDADES DE AUTENTICAÇÃO (IMPLEMENTAÇÃO CORRETA)
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True
    
    def get_session_auth_hash(self):
        return self.password

    # 🔴 CORREÇÃO FINAL: MÉTODO OBRIGATÓRIO
    
    def get_username(self):
        # O Django precisa deste método para identificar o usuário.
        # Você deve retornar o campo que usa para login (seu email).
        return self.email

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.name