"""
URL configuration for final_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from crud import views as crud_views
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='crud/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('edit_users/', crud_views.new_user, name='edit_users'),
    path('delete_user/<int:user_id>/', crud_views.delete_user, name='delete_user'),
    path('main-menu/', crud_views.main_menu, name='main_menu'),
    path('', auth_views.LoginView.as_view(template_name='crud/login.html'), name='login'),
    path('item/create/', crud_views.item_create, name='item_create'),
    path('item/<int:pk>/', crud_views.item_detail, name='item_detail'),
    path('item/<int:pk>/update/', crud_views.item_update, name='item_update'),
    path('item/<int:pk>/delete/', crud_views.item_delete, name='item_delete'),
    path('products/', crud_views.products_management, name='products_management'),
    path('cart/add/', crud_views.add_to_cart, name='add_to_cart'),
    path('cart/', crud_views.view_cart, name='view_cart'),
    path('cart/update_quantity/', crud_views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:pk>/', crud_views.remove_from_cart, name='remove_from_cart'),
    path('payment/', crud_views.payment_demo, name='payment_demo'),
    path('purchase_statistics/', crud_views.purchase_statistics, name='purchase_statistics'),
    path('profile_edit/', crud_views.profile_edit, name='profile_edit'),
    path('past_orders/', crud_views.past_orders, name='past_orders'),
    path('order_confirmation/', crud_views.order_confirmation, name='order_confirmation'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
