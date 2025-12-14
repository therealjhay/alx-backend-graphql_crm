import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
import re
from decimal import Decimal

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "orders")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock", "orders")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(default_value=0)

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)
    
    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(root, info, input):
        if input.phone and not re.match(r'^[\+\d\-\s]+$', input.phone):
            raise Exception("Invalid phone format")
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")
        customer = Customer.objects.create(
            name=input.name, email=input.email, phone=input.phone
        )
        return CreateCustomer(customer=customer, message="Customer created")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)
    
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(root, info, input):
        created_customers = []
        error_messages = []
        for data in input:
            try:
                if Customer.objects.filter(email=data.email).exists():
                    raise Exception(f"Email {data.email} exists")
                customer = Customer.objects.create(
                    name=data.name, email=data.email, phone=data.phone
                )
                created_customers.append(customer)
            except Exception as e:
                error_messages.append(str(e))
        return BulkCreateCustomers(customers=created_customers, errors=error_messages)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)
    
    product = graphene.Field(ProductType)

    def mutate(root, info, input):
        price_decimal = Decimal(str(input.price))
        if price_decimal <= 0:
            raise Exception("Price must be positive")
        product = Product.objects.create(
            name=input.name, price=price_decimal, stock=input.stock
        )
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)
    
    order = graphene.Field(OrderType)

    def mutate(root, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid Customer ID")
        products = Product.objects.filter(pk__in=input.product_ids)
        if not products.exists():
            raise Exception("No valid products found")
        order = Order.objects.create(customer=customer)
        order.products.set(products)
        order.total_amount = sum(p.price for p in products)
        order.save()
        return CreateOrder(order=order)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    def resolve_all_customers(root, info):
        return Customer.objects.all()