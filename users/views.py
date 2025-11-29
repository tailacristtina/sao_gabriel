from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Users
from .forms import RegisterForm, LoginForm


def perfil_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.info(request, "Faça login para acessar o perfil.")
        return redirect('users:login')

    try:
        user = Users.objects.get(id_users=user_id)
    except Users.DoesNotExist:
        messages.error(request, "Usuário não encontrado.")
        return redirect('users:login')

    return render(request, 'users/perfil.html', {'user': user})


def register_view(request):
    if request.method == 'POST':
        print("=== POST RECEBIDO ===")
        print(request.POST)

        form = RegisterForm(request.POST)
        if form.is_valid():
            print("=== FORMULÁRIO VÁLIDO ===")
            user = form.save()
            print("Usuário salvo:", user)

            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect('users:login')

        else:
            print("=== FORMULÁRIO INVÁLIDO ===")
            print(form.errors)
            messages.error(request, "Erro no cadastro. Verifique os dados e tente novamente.")
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Users.objects.get(email=email)

            if user.check_password(password):

                request.session['user_id'] = user.id_users
                request.session['user_name'] = user.name

                messages.success(request, f"Bem-vindo(a), {user.name}!")
                print(f"Usuário autenticado: {user.name}")

                if user.id_users == 1:
                    return redirect('/app_admin/dashboard/')
                else:
                    return redirect('store:index')

            else:
                messages.error(request, "Senha incorreta.")
                print("Senha incorreta.")

        except Users.DoesNotExist:
            messages.error(request, "Email não encontrado.")
            print("Email não encontrado.")

    return render(request, 'users/login.html')


def logout_view(request):
    request.session.flush()
    messages.info(request, "Você saiu da sua conta.")
    return redirect('users:login')


def home_view(request):
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')

    return render(request, 'index.html', {
        'user_id': user_id,
        'user_name': user_name
    })


def carrinho_view(request):
    return render(request, 'product/carrinho.html')