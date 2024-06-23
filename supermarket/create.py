import os
import django
import random
from django.utils import timezone
from faker import Faker
from datetime import timedelta

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supermarket.settings')
django.setup()

from main.models import User, Supplier, Category, Product, Order, OrderItem, Purchase, Sale

fake = Faker('ru_RU')  # Генерация данных на русском языке

# Создание пользователей
def create_users():
    roles = ['director', 'manager', 'warehouse_worker', 'cashier', 'customer']
    users = []

    # Создаем пользователей с различными ролями
    for role in roles:
        if role == 'director':
            num = 2  # 2 директора
        elif role == 'manager':
            num = 5  # 5 менеджеров
        elif role == 'warehouse_worker':
            num = 10  # 10 складских работников
        elif role == 'cashier':
            num = 15  # 15 кассиров
        else:
            num = 30  # 30 клиентов

        for _ in range(num):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123',
                role=role
            )
            users.append(user)

    return users

# Создание поставщиков
def create_suppliers():
    suppliers = []
    for _ in range(10):
        supplier = Supplier.objects.create(
            name=fake.company(),
            contact_info=fake.address()
        )
        suppliers.append(supplier)
    return suppliers

# Создание категорий и продуктов с логикой
def create_categories_and_products():
    categories_products = {
        'Электроника': [
            {'name': 'Смартфон', 'description': 'Мобильный телефон с сенсорным экраном и доступом в интернет'},
            {'name': 'Ноутбук', 'description': 'Переносной компьютер для работы и развлечений'},
            {'name': 'Телевизор', 'description': 'Цифровой телевизор с функцией Smart TV'},
            {'name': 'Наушники', 'description': 'Беспроводные наушники с шумоподавлением'},
            {'name': 'Камера', 'description': 'Цифровая камера для фото и видеосъемки'}
        ],
        'Одежда': [
            {'name': 'Футболка', 'description': 'Классическая хлопковая футболка'},
            {'name': 'Джинсы', 'description': 'Синие джинсы прямого кроя'},
            {'name': 'Куртка', 'description': 'Зимняя теплая куртка с капюшоном'},
            {'name': 'Платье', 'description': 'Летнее платье с цветочным принтом'},
            {'name': 'Кроссовки', 'description': 'Спортивные кроссовки для бега'}
        ],
        'Еда': [
            {'name': 'Хлеб', 'description': 'Свежий белый хлеб'},
            {'name': 'Молоко', 'description': 'Пастеризованное коровье молоко'},
            {'name': 'Яблоки', 'description': 'Сочные красные яблоки'},
            {'name': 'Картофель', 'description': 'Свежий картофель'},
            {'name': 'Рис', 'description': 'Длиннозернистый белый рис'}
        ],
        'Книги': [
            {'name': 'Роман', 'description': 'Художественный роман о любви и приключениях'},
            {'name': 'Научная книга', 'description': 'Книга о последних достижениях науки'},
            {'name': 'Учебник', 'description': 'Учебник по математике для школы'},
            {'name': 'Фантастика', 'description': 'Книга жанра научной фантастики'},
            {'name': 'Биография', 'description': 'Биография известного ученого'}
        ],
        'Мебель': [
            {'name': 'Стол', 'description': 'Деревянный обеденный стол'},
            {'name': 'Стул', 'description': 'Комфортный офисный стул'},
            {'name': 'Диван', 'description': 'Мягкий диван для гостиной'},
            {'name': 'Кровать', 'description': 'Двуспальная кровать с матрасом'},
            {'name': 'Шкаф', 'description': 'Шкаф для одежды с зеркалом'}
        ]
    }

    for category_name, products in categories_products.items():
        category = Category.objects.create(
            name=category_name,
            description=fake.text()
        )
        for product in products:
            Product.objects.create(
                name=product['name'],
                description=product['description'],
                price=round(random.uniform(10, 1000), 2),
                stock=random.randint(10, 200),
                category=category
            )

# Создание случайной даты за последние 2 месяца
def random_date_within_last_2_months():
    now = timezone.now()
    delta_days = random.randint(0, 60)
    return now - timedelta(days=delta_days)

# Создание заказов
def create_orders(users):
    orders = []
    products = list(Product.objects.all())
    for _ in range(100):
        user = random.choice([u for u in users if u.role == 'customer'])
        order = Order.objects.create(
            customer=user,
            total_price=0,
            date=random_date_within_last_2_months(),
            status=random.choice(['В ожидании', 'Завершён', 'Отменён'])
        )
        total_price = 0
        for _ in range(random.randint(1, 5)):
            product = random.choice(products)
            quantity = random.randint(1, 10)
            price = product.price * quantity
            total_price += price
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
        order.total_price = total_price
        order.save()
        orders.append(order)
    return orders

# Создание закупок
def create_purchases(suppliers):
    products = list(Product.objects.all())
    for _ in range(50):
        supplier = random.choice(suppliers)
        product = random.choice(products)
        quantity = random.randint(10, 100)
        price = round(random.uniform(10, 500), 2)
        total_price = quantity * price
        Purchase.objects.create(
            supplier=supplier,
            product=product,
            quantity=quantity,
            price=price,
            total_price=total_price,
            date=random_date_within_last_2_months()
        )

# Создание продаж
def create_sales(users):
    products = list(Product.objects.all())
    cashiers = [u for u in users if u.role in ['cashier', 'manager', 'warehouse_worker', 'director']]
    for _ in range(50):
        cashier = random.choice(cashiers)
        product = random.choice(products)
        quantity = random.randint(1, 20)
        price = product.price
        total_price = quantity * price
        Sale.objects.create(
            product=product,
            quantity=quantity,
            price=price,
            total_price=total_price,
            date=random_date_within_last_2_months(),
            cashier=cashier
        )

if __name__ == "__main__":
    users = create_users()
    suppliers = create_suppliers()
    create_categories_and_products()
    create_orders(users)
    create_purchases(suppliers)
    create_sales(users)
    print("База данных заполнена случайными данными на русском языке.")
