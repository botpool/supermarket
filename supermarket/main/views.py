from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
import json
from collections import defaultdict
from django.db.models import Sum, Q
from django.utils import timezone 
from .models import Product, Supplier, Purchase, Sale, Order, User, Category, SalesReport, Cart, CartItem, OrderItem
from .forms import ProductForm, SupplierForm, PurchaseForm, SaleForm, UserRegistrationForm, CategoryForm, CheckoutForm, OrderItemForm, OrderForm
from .decorators import exclude_customer

def home(request):
    search_query = request.GET.get('search', '')
    categories = Category.objects.all()
    filtered_categories = []
    
    for category in categories:
        filtered_products = category.product_set.filter(name__icontains=search_query)
        if filtered_products.exists():
            filtered_categories.append((category, filtered_products))
    
    return render(request, 'main/home.html', {
        'categories': filtered_categories,
        'search_query': search_query,
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'main/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return JsonResponse({'success': True})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return JsonResponse({'success': True})

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        quantity = int(data.get('quantity'))
        
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart_item.quantity = quantity
        cart_item.save()

        # Calculate new total for the item
        new_total = cart_item.product.price * cart_item.quantity

        # Calculate total price for the cart
        cart_items = cart_item.cart.items.all()
        cart_total = sum(item.product.price * item.quantity for item in cart_items)

        return JsonResponse({
            'success': True,
            'new_total': new_total,
            'cart_total': cart_total
        })
    return JsonResponse({'success': False})

# Добавьте функцию для оформления заказа
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            payment_method = form.cleaned_data['payment_method']
            order = Order.objects.create(
                customer=request.user,
                total_price=cart.total_price,
                date=timezone.now(),
                status='pending'
            )
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            cart.items.all().delete()  # Очистка корзины после оформления заказа
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm()
    return render(request, 'main/checkout.html', {'form': form, 'cart': cart})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'main/order_confirmation.html', {'order': order})
    
@login_required
@exclude_customer
def user_list(request):
    users = User.objects.all()
    return render(request, 'main/user_list.html', {'users': users})

@login_required
@exclude_customer
def product_list(request):
    products = Product.objects.all()
    return render(request, 'main/product_list.html', {'products': products})

@login_required
@exclude_customer
def add_product(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'main/product_form.html', {'form': form, 'categories': categories})

@login_required
@exclude_customer
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'main/product_form.html', {'form': form, 'categories': categories})

@login_required
@exclude_customer
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'main/product_confirm_delete.html', {'product': product})

@login_required
@exclude_customer
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'main/supplier_list.html', {'suppliers': suppliers})

@login_required
@exclude_customer
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'main/supplier_form.html', {'form': form})

@login_required
@exclude_customer
def edit_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'main/supplier_form.html', {'form': form})

@login_required
@exclude_customer
def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_list')
    return render(request, 'main/supplier_confirm_delete.html', {'supplier': supplier})

@login_required
@exclude_customer
def purchase_list(request):
    purchases = Purchase.objects.all()
    return render(request, 'main/purchase_list.html', {'purchases': purchases})

@login_required
@exclude_customer
def add_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('purchase_list')
    else:
        form = PurchaseForm()
    return render(request, 'main/purchase_form.html', {'form': form})

@login_required
@exclude_customer
def edit_purchase(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            form.save()
            return redirect('purchase_list')
    else:
        form = PurchaseForm(instance=purchase)
    return render(request, 'main/purchase_form.html', {'form': form})

@login_required
@exclude_customer
def delete_purchase(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    if request.method == 'POST':
        purchase.delete()
        return redirect('purchase_list')
    return render(request, 'main/purchase_confirm_delete.html', {'purchase': purchase})

@login_required
@exclude_customer
def sale_list(request):
    sales = Sale.objects.all()
    return render(request, 'main/sale_list.html', {'sales': sales})

@login_required
@exclude_customer
def add_sale(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sale_list')
    else:
        form = SaleForm()
    return render(request, 'main/sale_form.html', {'form': form})

@login_required
@exclude_customer
def edit_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            return redirect('sale_list')
    else:
        form = SaleForm(instance=sale)
    return render(request, 'main/sale_form.html', {'form': form})

@login_required
@exclude_customer
def delete_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        sale.delete()
        return redirect('sale_list')
    return render(request, 'main/sale_confirm_delete.html', {'sale': sale})

@login_required
@exclude_customer
def order_list(request):
    orders = Order.objects.all()
    return render(request, 'main/order_list.html', {'orders': orders})

@login_required
@exclude_customer
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user
            order.save()
            return redirect('order_list')
    else:
        form = OrderForm()
    return render(request, 'main/order_form.html', {'form': form})

@login_required
@exclude_customer
def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order_list')
    else:
        form = OrderForm(instance=order)
    return render(request, 'main/order_form.html', {'form': form})

@login_required
@exclude_customer
def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('order_list')
    return render(request, 'main/order_confirm_delete.html', {'order': order})

@login_required
@exclude_customer
def report_sales(request):
    sale_reports = Sale.objects.all().order_by('date')
    sales_by_date = defaultdict(list)
    totals_by_date = {}

    for sale in sale_reports:
        sale.total_cost = sale.total_price
        sales_by_date[sale.date].append(sale)

    for date, sales in sales_by_date.items():
        totals_by_date[date] = sum(sale.total_cost for sale in sales)

    return render(request, 'main/report_sales.html', {
        'sales_by_date': dict(sales_by_date),
        'totals_by_date': totals_by_date,
    })

@login_required
@exclude_customer
def report_purchases(request):
    purchase_reports = Purchase.objects.all().order_by('date')
    purchases_by_date = defaultdict(list)
    totals_by_date = {}

    for purchase in purchase_reports:
        purchase.total_cost = purchase.price * purchase.quantity
        purchases_by_date[purchase.date].append(purchase)

    for date, purchases in purchases_by_date.items():
        totals_by_date[date] = sum(purchase.total_cost for purchase in purchases)

    return render(request, 'main/report_purchases.html', {
        'purchases_by_date': dict(purchases_by_date),
        'totals_by_date': totals_by_date,
    })

@login_required
@exclude_customer
def report_orders(request):
    order_reports = Order.objects.all().order_by('date')
    orders_by_date = defaultdict(list)
    totals_by_date = {}

    for order in order_reports:
        orders_by_date[order.date].append(order)

    for date, orders in orders_by_date.items():
        totals_by_date[date] = sum(order.total_price for order in orders)

    return render(request, 'main/report_orders.html', {
        'orders_by_date': dict(orders_by_date),
        'totals_by_date': totals_by_date,
    })


@login_required
@exclude_customer
def product_catalog(request):
    query = request.GET.get('q')
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    categories = Category.objects.filter(product__in=products).distinct()

    return render(request, 'main/product_catalog.html', {
        'categories': categories,
        'products': products,
        'query': query,
    })

@login_required
@exclude_customer
def panel(request):
    return render(request, 'main/panel.html')

@login_required
@exclude_customer
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'main/category_list.html', {'categories': categories})

@login_required
@exclude_customer
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'main/category_form.html', {'form': form})

@login_required
@exclude_customer
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'main/category_form.html', {'form': form})

@login_required
@exclude_customer
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'main/category_confirm_delete.html', {'category': category})

@login_required
@exclude_customer
def manage_categories(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        if action == 'get':
            category_id = data.get('category_id')
            try:
                category = Category.objects.get(id=category_id)
                return JsonResponse({'id': category.id, 'name': category.name, 'description': category.description})
            except Category.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Category not found'})
        elif action == 'add':
            name = data.get('name')
            description = data.get('description')
            if name:
                Category.objects.create(name=name, description=description)
        elif action == 'edit':
            category_id = data.get('category_id')
            name = data.get('name')
            description = data.get('description')
            try:
                category = Category.objects.get(id=category_id)
                category.name = name
                category.description = description
                category.save()
            except Category.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Category not found'})
        elif action == 'delete':
            category_id = data.get('category_id')
            try:
                category = Category.objects.get(id=category_id)
                category.delete()
            except Category.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Category not found'})

        categories = Category.objects.all().values('id', 'name', 'description')
        return JsonResponse({'success': True, 'categories': list(categories)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def insufficient_permissions(request):
    return render(request, 'main/insufficient_permissions.html')
