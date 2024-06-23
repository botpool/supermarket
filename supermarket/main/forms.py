from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product, Supplier, Purchase, Sale, Order, OrderItem, Inventory, Warehouse, Shipment, Customer, OnlineOrder, OnlineOrderItem, SupplierContract, SalesReport, RestockRequest, Category, Cart, CartItem

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
            'role': 'Роль',
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'category']
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'price': 'Цена',
            'stock': 'Количество на складе',
            'category': 'Категория',
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_info']
        labels = {
            'name': 'Имя',
            'contact_info': 'Контактная информация',
        }

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['supplier', 'product', 'quantity', 'price', 'date']
        labels = {
            'supplier': 'Поставщик',
            'product': 'Товар',
            'quantity': 'Количество',
            'price': 'Цена',
            'date': 'Дата',
        }

class SaleForm(forms.ModelForm):
    cashier = forms.ModelChoiceField(queryset=User.objects.filter(role__in=['cashier', 'manager', 'warehouse_worker', 'director']), label='Кассир')
    
    class Meta:
        model = Sale
        fields = ['product', 'quantity', 'price', 'date', 'cashier']
        labels = {
            'product': 'Товар',
            'quantity': 'Количество',
            'price': 'Цена',
            'date': 'Дата',
            'cashier': 'Кассир',
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'total_price', 'date', 'status']
        labels = {
            'customer': 'Клиент',
            'total_price': 'Общая цена',
            'date': 'Дата',
            'status': 'Статус',
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'quantity']
        labels = {
            'order': 'Заказ',
            'product': 'Товар',
            'quantity': 'Количество',
        }

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['product', 'quantity', 'warehouse']
        labels = {
            'product': 'Товар',
            'quantity': 'Количество',
            'warehouse': 'Склад',
        }

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'location']
        labels = {
            'name': 'Название',
            'location': 'Местоположение',
        }

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['order', 'shipment_date', 'status']
        labels = {
            'order': 'Заказ',
            'shipment_date': 'Дата отправки',
            'status': 'Статус',
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address', 'password']
        labels = {
            'name': 'Имя',
            'email': 'Электронная почта',
            'phone': 'Телефон',
            'address': 'Адрес',
            'password': 'Пароль',
        }

class OnlineOrderForm(forms.ModelForm):
    class Meta:
        model = OnlineOrder
        fields = ['customer', 'order_date', 'status', 'total_amount']
        labels = {
            'customer': 'Клиент',
            'order_date': 'Дата заказа',
            'status': 'Статус',
            'total_amount': 'Общая сумма',
        }

class OnlineOrderItemForm(forms.ModelForm):
    class Meta:
        model = OnlineOrderItem
        fields = ['online_order', 'product', 'quantity', 'price']
        labels = {
            'online_order': 'Онлайн заказ',
            'product': 'Товар',
            'quantity': 'Количество',
            'price': 'Цена',
        }

class SupplierContractForm(forms.ModelForm):
    class Meta:
        model = SupplierContract
        fields = ['supplier', 'start_date', 'end_date', 'terms']
        labels = {
            'supplier': 'Поставщик',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'terms': 'Условия',
        }

class SalesReportForm(forms.ModelForm):
    class Meta:
        model = SalesReport
        fields = ['report_date', 'total_sales', 'total_customers']
        labels = {
            'report_date': 'Дата отчета',
            'total_sales': 'Общая сумма продаж',
            'total_customers': 'Общее количество клиентов',
        }

class RestockRequestForm(forms.ModelForm):
    class Meta:
        model = RestockRequest
        fields = ['product', 'quantity', 'request_date', 'status']
        labels = {
            'product': 'Товар',
            'quantity': 'Количество',
            'request_date': 'Дата запроса',
            'status': 'Статус',
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        labels = {
            'name': 'Название',
            'description': 'Описание',
        }

class CheckoutForm(forms.Form):
    address = forms.CharField(label='Адрес', max_length=255)
    payment_method = forms.ChoiceField(label='Метод оплаты', choices=[('cash', 'Наличные'), ('card', 'Карта')])
