import os
import django

# Настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supermarket.settings')
django.setup()

from main.models import User, Product, Category, Supplier, Purchase, Sale, Order, OrderItem, Cart, CartItem, Inventory, Warehouse, Shipment, Customer, OnlineOrder, OnlineOrderItem, SupplierContract, SalesReport, RestockRequest

# Удаление всех данных из всех таблиц, кроме пользователя с именем 'it-god'
User.objects.exclude(username='it-god').delete()
Product.objects.all().delete()
Category.objects.all().delete()
Supplier.objects.all().delete()
Purchase.objects.all().delete()
Sale.objects.all().delete()
Order.objects.all().delete()
OrderItem.objects.all().delete()
Cart.objects.all().delete()
CartItem.objects.all().delete()
Inventory.objects.all().delete()
Warehouse.objects.all().delete()
Shipment.objects.all().delete()
Customer.objects.all().delete()
OnlineOrder.objects.all().delete()
OnlineOrderItem.objects.all().delete()
SupplierContract.objects.all().delete()
SalesReport.objects.all().delete()
RestockRequest.objects.all().delete()

print("Все данные из всех таблиц, кроме пользователя 'it-god', были удалены.")
