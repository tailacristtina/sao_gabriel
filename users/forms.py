from django import forms
from .models import Users
from django.contrib.auth.hashers import make_password

class RegisterForm(forms.ModelForm):
    password_confirm = forms.CharField(widget=forms.PasswordInput(), label="Confirme a senha")

    class Meta:
        model = Users
        fields = ['name', 'birth', 'cpf', 'telephone', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email = forms.CharField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput(), label="Senha")