from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Category, Variety
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

@login_required
def main_menu(request):
    context = {'is_admin': request.user.is_staff}
    return render(request, 'crud/main_menu.html', context)

@login_required
def variety_list(request):
    varieties = Variety.objects.all()
    return render(request, 'crud/variety_list.html', {'varieties': varieties})

@login_required
def variety_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            if Variety.objects.filter(name=name).exists():
                messages.error(request, 'Variety with this name already exists.')
            else:
                Variety.objects.create(name=name)
                messages.success(request, 'Variety created successfully.')
                return redirect('variety_list')
        else:
            messages.error(request, 'Name cannot be empty.')
    return render(request, 'crud/variety_form.html')

@login_required
def variety_update(request, pk):
    variety = get_object_or_404(Variety, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            if Variety.objects.filter(name=name).exclude(pk=pk).exists():
                messages.error(request, 'Variety with this name already exists.')
            else:
                variety.name = name
                variety.save()
                messages.success(request, 'Variety updated successfully.')
                return redirect('variety_list')
        else:
            messages.error(request, 'Name cannot be empty.')
    return render(request, 'crud/variety_form.html', {'variety': variety})

@login_required
def variety_delete(request, pk):
    variety = get_object_or_404(Variety, pk=pk)
    if request.method == 'POST':
        variety.delete()
        messages.success(request, 'Variety deleted successfully.')
        return redirect('variety_list')
    return render(request, 'crud/variety_confirm_delete.html', {'variety': variety})

@login_required
def item_list(request):
    if not request.user.is_staff:
        return redirect('main_menu')
    items = Item.objects.all()
    return render(request, 'crud/item_list.html', {'items': items})

@login_required
def products_management(request):
    category_id = request.GET.get('category', '')
    search_query = request.GET.get('search', '')

    products = Item.objects.all()

    if category_id and category_id != 'all':
        products = products.filter(category_id=category_id)

    if search_query:
        products = products.filter(name__icontains=search_query)

    categories = Category.objects.all()

    return render(request, 'crud/products.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
    })

@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'crud/item_detail.html', {'item': item})

from django.contrib import messages

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
        variety_id = request.POST.get('variety', '')
        variety = None
        if variety_id:
            try:
                variety = Variety.objects.get(pk=variety_id)
            except Variety.DoesNotExist:
                variety = None
        category_name = request.POST.get('category', '').strip()
        category = None
        if category_name:
            category, created = Category.objects.get_or_create(name=category_name)
        quantity = int(request.POST.get('quantity', 0))
        Item.objects.create(name=name, description=description, variety=variety, category=category, quantity=quantity)
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
        if name != item.name and Item.objects.filter(name=name).exists():
            messages.error(request, "Product with this name already exists.")
            return render(request, 'crud/item_form.html', {'item': item})
        item.name = name
        item.description = request.POST.get('description')
        variety_id = request.POST.get('variety', '')
        if variety_id:
            try:
                variety = Variety.objects.get(pk=variety_id)
                item.variety = variety
            except Variety.DoesNotExist:
                item.variety = None
        else:
            item.variety = None
        category_name = request.POST.get('category', '').strip()
        if category_name:
            category, created = Category.objects.get_or_create(name=category_name)
            item.category = category
        else:
            item.category = None
        quantity = int(request.POST.get('quantity', 0))
        # Prevent negative values
        if quantity < 0:
            messages.error(request, "Quantity cannot be negative.")
            return render(request, 'crud/item_form.html', {'item': item})
        item.quantity = quantity
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
        if quantity > item.quantity:
            messages.error(request, f'Cannot add more than available quantity for {item.name}.')
            return redirect('products_management')
        cart = request.session.get('cart', {})
        current_quantity = cart.get(str(item_id), 0)
        if current_quantity + quantity > item.quantity:
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

from .models import Purchase
from django.db.models import Sum
from django.utils.timezone import now

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
                # Create Purchase record
                Purchase.objects.create(user=request.user, item=item, quantity=quantity)
            else:
                messages.error(request, f'Not enough quantity for {item.name}.')
                return redirect('view_cart')
        messages.success(request, 'Payment processed successfully.')
        # Clear cart after payment
        request.session['cart'] = {}
        return redirect('products_management')
    return render(request, 'crud/payment.html')

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def purchase_statistics(request):
    purchases = Purchase.objects.select_related('user', 'item').order_by('-purchase_date')
    # Aggregate total quantity per item
    total_per_item = Purchase.objects.values('item__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')
    context = {
        'purchases': purchases,
        'total_per_item': total_per_item,
        'now': now(),
    }
    return render(request, 'crud/purchase_statistics.html', context)

from django.contrib.auth.decorators import login_required

@login_required
def new_user(request):
    if not request.user.is_staff:
        return redirect('main_menu')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        username = request.POST.get('username')
        role = request.POST.get('role')
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
            if password and password.strip() != '':
                user.set_password(password)
            # If password is empty or not provided, do not change the password
            # Role update logic
            if request.user.is_superuser:
                # Admin can set user, staff or admin
                if role == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                elif role == 'staff':
                    user.is_staff = True
                    user.is_superuser = False
                else:
                    user.is_staff = False
                    user.is_superuser = False
            elif request.user.is_staff:
                # Staff can only set admin or user
                if role == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                elif role == 'user':
                    user.is_staff = False
                    user.is_superuser = False
                else:
                    return render(request, 'crud/new_user.html', {'error': 'Staff can only create admin or user roles', 'users': User.objects.all()})
            user.save()
            return redirect('edit_users')
        else:
            # Create new user
            if username and User.objects.filter(username=username).exists():
                users = User.objects.all()
                return render(request, 'crud/new_user.html', {'error': 'Username already exists', 'users': users})
            password = request.POST.get('password')
            if username and password:
                if request.user.is_superuser:
                    # Admin can create user, staff or admin
                    if role == 'admin':
                        user = User.objects.create_user(username=username, password=password, is_staff=True, is_superuser=True)
                    elif role == 'staff':
                        user = User.objects.create_user(username=username, password=password, is_staff=True, is_superuser=False)
                    else:
                        user = User.objects.create_user(username=username, password=password, is_staff=False, is_superuser=False)
                elif request.user.is_staff:
                    # Staff can only create admin or user
                    if role == 'admin':
                        user = User.objects.create_user(username=username, password=password, is_staff=True, is_superuser=True)
                    elif role == 'user':
                        user = User.objects.create_user(username=username, password=password, is_staff=False, is_superuser=False)
                    else:
                        return render(request, 'crud/new_user.html', {'error': 'Staff can only create admin or user roles', 'users': User.objects.all()})
                else:
                    return render(request, 'crud/new_user.html', {'error': 'You do not have permission to create users', 'users': User.objects.all()})
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
