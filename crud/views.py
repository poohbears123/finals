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
    products = Item.objects.all()
    return render(request, 'crud/products.html', {'products': products})

@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'crud/item_detail.html', {'item': item})

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Item
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

@login_required
def item_create(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to add products.")
        return redirect('products_management')
    if request.method == 'POST':
        name = request.POST.get('name')
        if Item.objects.filter(name=name).exists():
            messages.error(request, "Product with this name already exists.")
            return render(request, 'crud/item_form.html')
        description = request.POST.get('description')
        variety = request.POST.get('variety', '')
        total_quantity = int(request.POST.get('total_quantity', 0))
        quantity_remain = int(request.POST.get('quantity_remain', 0))
        Item.objects.create(name=name, description=description, variety=variety, total_quantity=total_quantity, quantity_remain=quantity_remain)
        return redirect('products_management')
    return render(request, 'crud/item_form.html')

from django.contrib import messages

@login_required
def item_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to update products.")
        return redirect('products_management')
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        # Allow unchanged name without error
        if name != item.name and Item.objects.filter(name=name).exists():
            messages.error(request, "Product with this name already exists.")
            return render(request, 'crud/item_form.html', {'item': item})
        item.name = name
        item.description = request.POST.get('description')
        item.variety = request.POST.get('variety', '')
        total_quantity = int(request.POST.get('total_quantity', 0))
        quantity_remain = int(request.POST.get('quantity_remain', 0))
        # Prevent negative values
        if total_quantity < 0 or quantity_remain < 0:
            messages.error(request, "Total quantity and quantity remain cannot be negative.")
            return render(request, 'crud/item_form.html', {'item': item})
        item.total_quantity = total_quantity
        item.quantity_remain = quantity_remain
        item.save()
        messages.success(request, "Product updated successfully.")
        return redirect('products_management')
    return render(request, 'crud/item_form.html', {'item': item})

@login_required
def item_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to delete products.")
        return redirect('products_management')
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('products_management')
    return render(request, 'crud/item_confirm_delete.html', {'item': item})

from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        if not item_id:
            messages.error(request, 'No item specified.')
            return redirect('products_management')
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            messages.error(request, 'Invalid quantity.')
            return redirect('products_management')
        if quantity < 1:
            messages.error(request, 'Quantity must be at least 1.')
            return redirect('products_management')
        item = get_object_or_404(Item, pk=item_id)
        if quantity > item.quantity_remain:
            messages.error(request, f'Cannot add more than available quantity for {item.name}.')
            return redirect('products_management')
        cart = request.session.get('cart', {})
        current_quantity = cart.get(str(item_id), 0)
        if current_quantity + quantity > item.quantity_remain:
            messages.error(request, f'Cannot add more than available quantity for {item.name}.')
            return redirect('products_management')
        cart[str(item_id)] = current_quantity + quantity
        request.session['cart'] = cart
        messages.success(request, f'Added {quantity} of {item.name} to cart.')
        return redirect('products_management')
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('products_management')

@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total_quantity = 0
    for pk, quantity in cart.items():
        item = get_object_or_404(Item, pk=pk)
        items.append({'item': item, 'quantity': quantity})
        total_quantity += quantity
    return render(request, 'crud/cart.html', {'items': items, 'total_quantity': total_quantity})

@login_required
def update_cart_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1
        item = get_object_or_404(Item, pk=item_id)
        if quantity < 1:
            quantity = 1
        if quantity > item.quantity_remain:
            quantity = item.quantity_remain
        cart = request.session.get('cart', {})
        cart[str(item_id)] = quantity
        request.session['cart'] = cart
        messages.success(request, f'Updated quantity for {item.name} to {quantity}.')
        return redirect('view_cart')
    else:
        return redirect('view_cart')

@login_required
def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        del cart[str(pk)]
        request.session['cart'] = cart
        messages.success(request, 'Item removed from cart.')
    return redirect('view_cart')

@login_required
def payment_demo(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        for pk_str, quantity in cart.items():
            pk = int(pk_str)
            item = get_object_or_404(Item, pk=pk)
            if item.quantity_remain >= quantity:
                item.quantity_remain -= quantity
                item.save()
            else:
                messages.error(request, f'Not enough quantity for {item.name}.')
                return redirect('view_cart')
        messages.success(request, 'Payment processed successfully.')
        # Clear cart after payment
        request.session['cart'] = {}
        return redirect('products_management')
    return render(request, 'crud/payment.html')

from django.contrib.auth.decorators import login_required

@login_required
def new_user(request):
    if not request.user.is_staff:
        return redirect('main_menu')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        username = request.POST.get('username')
        if user_id:
            # Edit existing user
            user = get_object_or_404(User, id=user_id)
            if username and User.objects.filter(username=username).exclude(id=user_id).exists():
                users = User.objects.all()
                return render(request, 'crud/new_user.html', {'error': 'Username already exists', 'users': users})
            if username:
                user.username = username
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            password = request.POST.get('password')
            if password:
                user.set_password(password)
            user.save()
            return redirect('edit_users')
        else:
            # Create new user
            if username and User.objects.filter(username=username).exists():
                users = User.objects.all()
                return render(request, 'crud/new_user.html', {'error': 'Username already exists', 'users': users})
            password = request.POST.get('password')
            if username and password:
                user = User.objects.create_user(username=username, password=password)
                user.first_name = request.POST.get('first_name', '')
                user.last_name = request.POST.get('last_name', '')
                user.email = request.POST.get('email', '')
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
