from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=255, required=True)
    birth = forms.DateField(required=True)
    cpf = forms.CharField(max_length=11, required=True)
    telephone = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

        user_profile = UserProfile(user=user, 
                                   name=self.cleaned_data['name'], 
                                   birth=self.cleaned_data['birth'], 
                                   cpf=self.cleaned_data['cpf'], 
                                   telephone=self.cleaned_data['telephone'])
        user_profile.save()
        return user
