from django.shortcuts import render, get_object_or_404, redirect
from .models import Item
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

@login_required
def main_menu(request):
    return render(request, 'crud/main_menu.html')

def item_list(request):
    items = Item.objects.all()
    return render(request, 'crud/item_list.html', {'items': items})

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'crud/item_detail.html', {'item': item})

def item_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        Item.objects.create(name=name, description=description)
        return redirect('item_list')
    return render(request, 'crud/item_form.html')

def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.save()
        return redirect('item_list')
    return render(request, 'crud/item_form.html', {'item': item})

def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'crud/item_confirm_delete.html', {'item': item})

def new_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            return redirect('login')
        else:
            return render(request, 'crud/new_user.html', {'error': 'Please provide username and password'})
    return render(request, 'crud/new_user.html')

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('login')
    return render(request, 'crud/delete_user_confirm.html', {'user': user})
