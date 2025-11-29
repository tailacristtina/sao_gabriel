from django.contrib.auth.hashers import make_password, check_password
from django.db import models

class Users(models.Model):
    id_users = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    birth = models.CharField(max_length=10)
    cpf = models.CharField(max_length=11, unique=True)
    telephone = models.CharField(max_length=12)
    email = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=200)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    class Meta:
        db_table = 'users'