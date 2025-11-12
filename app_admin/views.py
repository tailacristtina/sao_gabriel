from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product

def admin_dashboard(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "Você precisa fazer login.")
        return redirect('login')

    if user_id != 1:
        messages.error(request, "Acesso negado: apenas administradores podem acessar.")
        return redirect('index')

    return render(request, 'administrator/admin_dashboard.html', {
        'titulo_gerenciamento': 'Painel do Administrador',
    })

def product_list(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "Você precisa fazer login.")
        return redirect('login')

    if user_id != 1:
        messages.error(request, "Acesso negado: apenas administradores podem acessar.")
        return redirect('index')

    products = Product.objects.all()
    context = {
        'products': products,
        'titulo_gerenciamento': 'Gerenciar Produtos',
    }
    return render(request, 'administrator/product_list.html', context)


def product_create(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "Você precisa fazer login.")
        return redirect('login')

    if user_id != 1:
        messages.error(request, "Acesso negado: apenas administradores podem acessar.")
        return redirect('index')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')

        if not name or not price:
            messages.error(request, "Nome e preço são obrigatórios.")
        else:
            Product.objects.create(
                name=name,
                description=description,
                price=price
            )
            messages.success(request, f"Produto '{name}' criado com sucesso!")
            return redirect('product_list')

    return render(request, 'administrator/product_form.html', {
        'titulo_gerenciamento': 'Cadastrar Novo Produto',
    })


def product_edit(request, product_id):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "Você precisa fazer login.")
        return redirect('login')

    if user_id != 1:
        messages.error(request, "Acesso negado: apenas administradores podem acessar.")
        return redirect('index')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')

        if not name or not price:
            messages.error(request, "Nome e preço são obrigatórios.")
        else:
            product.name = name
            product.description = description
            product.price = price
            product.save()
            messages.success(request, f"Produto '{name}' atualizado com sucesso!")
            return redirect('product_list')

    return render(request, 'administrator/product_form.html', {
        'product': product,
        'titulo_gerenciamento': f'Editar Produto: {product.name}',
    })


def product_delete(request, product_id):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "Você precisa fazer login.")
        return redirect('login')

    if user_id != 1:
        messages.error(request, "Acesso negado: apenas administradores podem acessar.")
        return redirect('index')

    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, f"Produto '{product.name}' excluído com sucesso!")
    return redirect('product_list')
