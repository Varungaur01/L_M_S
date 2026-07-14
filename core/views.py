from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import User, Product, Cart, CartItem, Order, OrderItem
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.http import HttpResponseForbidden

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role',)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Detailed description...', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price (e.g. 50.00)'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Image URL (Optional)'}),
        }

def explore(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'core/explore.html', {'products': products})

from django.db import IntegrityError

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                return redirect('explore')
            except IntegrityError:
                form.add_error('username', 'This username is already taken.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'SHOPKEEPER':
                return redirect('dashboard')
            return redirect('explore')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('explore')

@login_required
def dashboard(request):
    if request.user.role != 'SHOPKEEPER':
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    products = Product.objects.filter(shopkeeper=request.user)
    return render(request, 'core/dashboard.html', {'products': products})

@login_required
def add_product(request):
    if request.user.role != 'SHOPKEEPER':
        return HttpResponseForbidden("Only shopkeepers can add products.")
    
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.shopkeeper = request.user
            product.save()
            messages.success(request, "Product added successfully!")
            return redirect('dashboard')
    else:
        form = ProductForm()
    return render(request, 'core/add_product.html', {'form': form})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    messages.success(request, f"{product.name} added to cart.")
    return redirect('explore')

@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    total = sum(item.product.price * item.quantity for item in items)
    return render(request, 'core/cart.html', {'items': items, 'total': total})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('view_cart')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.all()
    if not items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('explore')
        
    total = sum(item.product.price * item.quantity for item in items)
    order = Order.objects.create(user=request.user, total_price=total)
    
    for item in items:
        OrderItem.objects.create(
            order=order, 
            product=item.product, 
            quantity=item.quantity, 
            price_at_checkout=item.product.price
        )
        
    items.delete()
    messages.success(request, "Order placed successfully! We will coordinate delivery shortly.")
    return redirect('explore')

@login_required
def admin_dashboard(request):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Only administrators can view this page.")
        
    orders = Order.objects.all().order_by('-created_at')
    delivery_boys = User.objects.filter(role='DELIVERY')
    return render(request, 'core/admin_dashboard.html', {'orders': orders, 'delivery_boys': delivery_boys})

@login_required
def assign_order(request, order_id):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Only administrators can assign orders.")
        
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        boy_id = request.POST.get('delivery_boy')
        if boy_id:
            boy = get_object_or_404(User, id=boy_id, role='DELIVERY')
            order.delivery_boy = boy
            order.status = 'ASSIGNED'
            order.save()
            messages.success(request, f"Order #{order.id} assigned to {boy.username}.")
            
    return redirect('admin_dashboard')

@login_required
def delivery_dashboard(request):
    if request.user.role != 'DELIVERY':
        return HttpResponseForbidden("Only delivery personnel can view this.")
        
    assigned_orders = request.user.deliveries.exclude(status='DELIVERED').order_by('-created_at')
    past_orders = request.user.deliveries.filter(status='DELIVERED').order_by('-created_at')
    return render(request, 'core/delivery_dashboard.html', {'assigned_orders': assigned_orders, 'past_orders': past_orders})

@login_required
def update_order_status(request, order_id):
    if request.user.role != 'DELIVERY':
        return HttpResponseForbidden("Only delivery personnel can update status.")
        
    order = get_object_or_404(Order, id=order_id, delivery_boy=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.id} status updated to {new_status}.")
            
    return redirect('delivery_dashboard')

