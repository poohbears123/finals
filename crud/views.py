from django.shortcuts import render, get_object_or_404, redirect
from .models import Item
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

@login_required
def main_menu(request):
    context = {'is_admin': request.user.is_staff}
    return render(request, 'crud/main_menu.html', context)

@login_required
def item_list(request):
    if not request.user.is_staff:
        return redirect('main_menu')
    items = Item.objects.all()
    return render(request, 'crud/item_list.html', {'items': items})

@login_required
def products_management(request):
    if not request.user.is_staff:
        return redirect('main_menu')
    products = Item.objects.all()
    return render(request, 'crud/products.html', {'products': products})

@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'crud/item_detail.html', {'item': item})

@login_required
def item_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        variety = request.POST.get('variety', '')
        total_quantity = int(request.POST.get('total_quantity', 0))
        quantity_remain = int(request.POST.get('quantity_remain', 0))
        Item.objects.create(name=name, description=description, variety=variety, total_quantity=total_quantity, quantity_remain=quantity_remain)
        return redirect('item_list')
    return render(request, 'crud/item_form.html')

@login_required
def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.variety = request.POST.get('variety', '')
        item.total_quantity = int(request.POST.get('total_quantity', 0))
        item.quantity_remain = int(request.POST.get('quantity_remain', 0))
        item.save()
        return redirect('item_list')
    return render(request, 'crud/item_form.html', {'item': item})

@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'crud/item_confirm_delete.html', {'item': item})

from django.contrib.auth.decorators import login_required

@login_required
def new_user(request):
    if not request.user.is_staff:
        return redirect('main_menu')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        username = request.POST.get('username')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        if user_id:
            # Edit existing user
            user = get_object_or_404(User, id=user_id)
            if username:
                user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            if password:
                user.set_password(password)
            user.save()
            return redirect('edit_users')
        else:
            # Create new user
            if username and password:
                user = User.objects.create_user(username=username, password=password)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()
                return redirect('edit_users')
            else:
                users = User.objects.all()
                return render(request, 'crud/new_user.html', {'error': 'Please provide username and password', 'users': users})
    users = User.objects.all()
    return render(request, 'crud/new_user.html', {'users': users})

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('login')
    return render(request, 'crud/delete_user_confirm.html', {'user': user})
