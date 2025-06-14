import logging
from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Category, Variety
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

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
                variety = Variety.objects.create(name=name)
                logger.info(f"Variety added: {variety.name} (ID: {variety.id})")
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
                logger.info(f"Variety updated: {variety.name} (ID: {variety.id})")
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

from django.core.paginator import Paginator

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

    paginator = Paginator(products, 6)  # Show 6 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'crud/products.html', {
        'products': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
        'page_obj': page_obj,
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
            return render(request, 'crud/item_form.html', {'size_options': ['S', 'M', 'L', 'XL', 'XXL']})
        description = request.POST.get('description')
        variety_name = request.POST.get('variety', '').strip()
        variety = None
        if variety_name:
            variety, created = Variety.objects.get_or_create(name=variety_name)
        category_name = request.POST.get('category', '').strip()
        category = None
        if category_name:
            category, created = Category.objects.get_or_create(name=category_name)
        size = request.POST.get('size', 'M')
        stock = int(request.POST.get('stock', 0))
        price = int(request.POST.get('price', 0))
        photo = request.FILES.get('photo')
        item = Item.objects.create(name=name, description=description, variety=variety, category=category, size=size, stock=stock, price=price, photo=photo)
        logger.info(f"Item added: {item.name} (ID: {item.id})")
        return redirect('products_management')
    return render(request, 'crud/item_form.html', {'size_options': ['S', 'M', 'L', 'XL', 'XXL']})

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
            return render(request, 'crud/item_form.html', {'item': item, 'size_options': ['S', 'M', 'L', 'XL', 'XXL']})
        item.name = name
        item.description = request.POST.get('description')
        variety_name = request.POST.get('variety', '').strip()
        if variety_name:
            variety, created = Variety.objects.get_or_create(name=variety_name)
            item.variety = variety
        else:
            item.variety = None
        category_name = request.POST.get('category', '').strip()
        if category_name:
            category, created = Category.objects.get_or_create(name=category_name)
            item.category = category
        else:
            item.category = None
        size = request.POST.get('size', 'M')
        item.size = size
        stock = int(request.POST.get('stock', 0))
        # Prevent negative values
        if stock < 0:
            messages.error(request, "Stock cannot be negative.")
            return render(request, 'crud/item_form.html', {'item': item, 'size_options': ['S', 'M', 'L', 'XL', 'XXL']})
        item.stock = stock
        price = int(request.POST.get('price', 0))
        if price < 0:
            messages.error(request, "Price cannot be negative.")
            return render(request, 'crud/item_form.html', {'item': item, 'size_options': ['S', 'M', 'L', 'XL', 'XXL']})
        item.price = price
        photo = request.FILES.get('photo')
        if photo:
            item.photo = photo
        item.save()
        logger.info(f"Item updated: {item.name} (ID: {item.id})")
        messages.success(request, "Product updated successfully.")
        return redirect('products_management')
    return render(request, 'crud/item_form.html', {'item': item, 'size_options': ['S', 'M', 'L', 'XL', 'XXL']})

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
        size = request.POST.get('size', 'S')
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
            messages.error(request, f'Cannot add more than available stock for {item.name}.')
            return redirect('products_management')
        cart = request.session.get('cart', {})

        # Use combined key of item_id and size
        key = f"{item_id}_{size}"
        current_quantity = cart.get(key, 0)
        if current_quantity + quantity > item.quantity_remain:
            messages.error(request, f'Cannot add more than available stock for {item.name} size {size}.')
            return redirect('products_management')
        cart[key] = current_quantity + quantity
        request.session['cart'] = cart
        messages.success(request, f'Added {quantity} of {item.name} size {size} to cart.')
        return redirect('products_management')
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('products_management')

@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total_quantity = 0
    total_price = 0
    for key, quantity in cart.items():
        # key format: item_id_size
        parts = key.split('_')
        if len(parts) == 2:
            item_id, size = parts
        else:
            item_id = parts[0]
            size = 'S'  # default size if not specified
        item = get_object_or_404(Item, pk=item_id)
        item_total_price = item.price * quantity
        items.append({'item': item, 'quantity': quantity, 'item_total_price': item_total_price, 'size': size})
        total_quantity += quantity
        total_price += item_total_price

    # Fetch recent purchases by status for the user (last 5 each)
    completed_orders = Purchase.objects.filter(user=request.user, status='Completed').order_by('-purchase_date')[:5]
    pending_orders = Purchase.objects.filter(user=request.user, status='Pending').order_by('-purchase_date')[:5]
    ready_for_pickup_orders = Purchase.objects.filter(user=request.user, status='Ready for Pick Up').order_by('-purchase_date')[:5]

    return render(request, 'crud/cart.html', {
        'items': items,
        'total_quantity': total_quantity,
        'total_price': total_price,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'ready_for_pickup_orders': ready_for_pickup_orders,
    })

@login_required
def update_cart_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        new_size = request.POST.get('size', 'S')
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

        # Find old key for this item (any size)
        old_key = None
        for key in cart.keys():
            if key.startswith(f"{item_id}_"):
                old_key = key
                break

        if old_key and old_key != f"{item_id}_{new_size}":
            # Remove old key and add new key with updated size
            del cart[old_key]
            cart[f"{item_id}_{new_size}"] = quantity
        else:
            cart[f"{item_id}_{new_size}"] = quantity

        request.session['cart'] = cart
        messages.success(request, f'Updated quantity for {item.name} size {new_size} to {quantity}.')
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
from django.contrib.admin.views.decorators import staff_member_required
from .utils import send_to_zapier

@login_required
def order_summary(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('view_cart')

    items = []
    total_quantity = 0
    total_price = 0
    for key, quantity in cart.items():
        # key format: item_id_size
        parts = key.split('_')
        if len(parts) == 2:
            item_id, size = parts
        else:
            item_id = parts[0]
            size = 'S' 
        item = get_object_or_404(Item, pk=item_id)
        item_total_price = item.price * quantity
        items.append({'item': item, 'quantity': quantity, 'item_total_price': item_total_price, 'size': size})
        total_quantity += quantity
        total_price += item_total_price

    response = render(request, 'crud/order_summary.html', {
        'items': items,
        'total_quantity': total_quantity,
        'total_price': total_price,
    })
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@login_required
def payment_demo(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        order_details = []
        total_quantity = 0
        total_price = 0
        for key, quantity in cart.items():
            # key format: item_id_size
            parts = key.split('_')
            if len(parts) == 2:
                pk_str, size = parts
            else:
                pk_str = parts[0]
                size = 'S'  # default size if not specified
            pk = int(pk_str)
            item = get_object_or_404(Item, pk=pk)
            if item.quantity_remain >= quantity:
                item.stock -= quantity  
                item.save()
                purchase = Purchase.objects.create(user=request.user, item=item, quantity=quantity, status='Pending')
                logger.info(f"Purchase added: User {request.user.username}, Item {item.name} (ID: {item.id}), Quantity {quantity}")
                order_details.append({
                    'item_name': item.name,
                    'size': size,
                    'quantity': quantity,
                    'price': item.price,
                    'total_price': item.price * quantity,
                    'status': purchase.status,
                })
                total_quantity += quantity
                total_price += item.price * quantity
            else:
                messages.error(request, f'Not enough stock for {item.name}.')
                return redirect('order_summary')
        messages.success(request, 'Payment processed successfully.')
        request.session['cart'] = {}

        # Send order confirmation to Zapier
        payload = {
            'user': request.user.username,
            'full_name': f"{request.user.first_name} {request.user.last_name}".strip(),
            'email': request.user.email,
            'order_details': order_details,
            'total_quantity': total_quantity,
            'total_price': total_price,
            'purchase_date': purchase.purchase_date.isoformat() if order_details else None,
        }
        send_to_zapier(payload)

        return redirect('order_confirmation')
    return render(request, 'crud/payment.html')

from django.contrib.admin.views.decorators import staff_member_required

from django.core.paginator import Paginator
from django.db.models import Q

@staff_member_required
def purchase_statistics(request):
    search_query = request.GET.get('search', '').strip()

    purchases_qs = Purchase.objects.select_related('user', 'item').order_by('-purchase_date')
    if search_query:
        purchases_qs = purchases_qs.filter(
            Q(user__username__icontains=search_query) |
            Q(item__name__icontains=search_query) |
            Q(status__icontains=search_query)
        )

    total_per_item_qs = Purchase.objects.values('item__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')

    # Pagination
    purchases_paginator = Paginator(purchases_qs, 15)
    total_per_item_paginator = Paginator(total_per_item_qs, 10)

    purchases_page_number = request.GET.get('purchases_page')
    total_per_item_page_number = request.GET.get('items_page')

    purchases = purchases_paginator.get_page(purchases_page_number)
    total_per_item = total_per_item_paginator.get_page(total_per_item_page_number)

    context = {
        'purchases': purchases,
        'total_per_item': total_per_item,
        'search_query': search_query,
        'now': now(),
    }
    return render(request, 'crud/purchase_statistics.html', context)

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from .models import Purchase
from django.contrib import messages

@login_required
def edit_users(request):
    if not request.user.is_staff:
        return redirect('main_menu')

    user_id = request.GET.get('user_id')
    profile_edit = False
    user_obj = None

    if user_id:
        try:
            user_obj = User.objects.get(id=user_id)
            profile_edit = True
        except User.DoesNotExist:
            user_obj = None
            profile_edit = False

    if request.method == 'POST':
        if profile_edit and user_obj:
            # Update existing user
            username = request.POST.get('username')
            if username and User.objects.filter(username=username).exclude(id=user_obj.id).exists():
                messages.error(request, 'Username already exists')
                return render(request, 'crud/new_user.html', {'user': user_obj, 'profile_edit': True, 'users': User.objects.all()})
            user_obj.username = username
            user_obj.first_name = request.POST.get('first_name', '')
            user_obj.last_name = request.POST.get('last_name', '')
            user_obj.email = request.POST.get('email', '')
            password = request.POST.get('password')
            if password and password.strip() != '':
                user_obj.set_password(password)
            role = request.POST.get('role')
            if role == 'admin':
                user_obj.is_superuser = True
                user_obj.is_staff = True
            elif role == 'staff':
                user_obj.is_superuser = False
                user_obj.is_staff = True
            else:
                user_obj.is_superuser = False
                user_obj.is_staff = False
            user_obj.save()
            logger.info(f"User updated: {user_obj.username} (ID: {user_obj.id})")
            messages.success(request, 'User updated successfully')
            return redirect('edit_users')
        else:
            # Create new user
            username = request.POST.get('username')
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return render(request, 'crud/new_user.html', {'users': User.objects.all()})
            password = request.POST.get('password')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            email = request.POST.get('email', '')
            role = request.POST.get('role')
            is_superuser = False
            is_staff = False
            if role == 'admin':
                is_superuser = True
                is_staff = True
            elif role == 'staff':
                is_superuser = False
                is_staff = True
            user_obj = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email, is_superuser=is_superuser, is_staff=is_staff)
            logger.info(f"User added: {user_obj.username} (ID: {user_obj.id})")
            messages.success(request, 'User created successfully')
            return redirect('edit_users')

    return render(request, 'crud/new_user.html', {'user': user_obj, 'profile_edit': profile_edit, 'users': User.objects.all()})

@login_required
def order_confirmation(request):
    return render(request, 'crud/order_confirmation.html')

@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        username = request.POST.get('username')
        if username and User.objects.filter(username=username).exclude(id=user.id).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'crud/new_user.html', {'user': user, 'profile_edit': True})
        if username:
            user.username = username
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        password = request.POST.get('password')
        if password and password.strip() != '':
            user.set_password(password)
        user.save()
        logger.info(f"User profile updated: {user.username} (ID: {user.id})")
        messages.success(request, 'Profile updated successfully')
        return redirect('profile_edit')
    return render(request, 'crud/new_user.html', {'user': user, 'profile_edit': True})

from django.core.paginator import Paginator

@login_required
def past_orders(request):
    search_query = request.GET.get('search', '').strip()
    purchases_list = Purchase.objects.filter(user=request.user).select_related('item').order_by('-purchase_date')
    if search_query:
        purchases_list = purchases_list.filter(
            item__name__icontains=search_query
        )
    paginator = Paginator(purchases_list, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    purchases = paginator.get_page(page_number)
    context = {
        'purchases': purchases,
        'search_query': search_query,
    }
    return render(request, 'crud/past_orders.html', context)

from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Purchase

from django.core.paginator import Paginator

@staff_member_required
@csrf_protect
def admin_orders(request):
    def send_full_update_to_zapier(purchases):
        payload = {
            'type': 'full_update',
            'updated_purchases': []
        }
        for purchase in purchases:
            payload['updated_purchases'].append({
                'purchase_id': purchase.id,
                'user': purchase.user.username,
                'full_name': f"{purchase.user.first_name} {purchase.user.last_name}".strip(),
                'email': purchase.user.email,
                'item': purchase.item.name,
                'quantity': purchase.quantity,
                'status': purchase.status,
                'purchase_date': purchase.purchase_date.isoformat(),
                'price': purchase.item.price,
            })
        from .utils import send_to_zapier
        send_to_zapier(payload)

    if request.method == 'POST':
        updated_count = 0
        updated_purchases = []
        for key, value in request.POST.items():
            if key.startswith('status_'):
                try:
                    purchase_id = int(key.split('_')[1])
                    purchase = Purchase.objects.get(id=purchase_id)
                    if purchase.status != value:
                        purchase.status = value
                        purchase.save()
                        updated_purchases.append(purchase)
                        print(f"Purchase updated: ID {purchase.id}, New status: {value}")  # Print to console
                        updated_count += 1
                except (Purchase.DoesNotExist, ValueError):
                    continue
        if updated_count > 0:
            send_full_update_to_zapier(updated_purchases)
            messages.success(request, f"{updated_count} order(s) updated successfully.")
        else:
            messages.info(request, "No orders were updated.")
        return redirect('admin_orders')
    else:
        purchases_list = Purchase.objects.select_related('user', 'item').exclude(status='Completed').order_by('-purchase_date')
        paginator = Paginator(purchases_list, 10)  # 10 orders per page
        page_number = request.GET.get('page')
        purchases = paginator.get_page(page_number)
        return render(request, 'crud/admin_orders.html', {'purchases': purchases})

from django.contrib import messages

@login_required
def delete_user(request, user_id):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "You do not have permission to delete users.")
        return redirect('main_menu')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('new_users')
    return render(request, 'crud/delete_user_confirm.html', {'user': user})
