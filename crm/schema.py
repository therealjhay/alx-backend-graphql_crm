import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter  # Import our new filters
import re
from decimal import Decimal

# --- 1. OUTPUT TYPES (Updated for Relay/Filtering) ---

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        # 'interfaces' tells Graphene this is a Relay Node (supports edges/pagination)
        interfaces = (graphene.relay.Node, )
        fields = ("id", "name", "email", "phone", "orders", "created_at")
        filterset_class = CustomerFilter

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node, )
        fields = ("id", "name", "price", "stock", "orders")
        filterset_class = ProductFilter

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node, )
        fields = ("id", "customer", "products", "order_date", "total_amount")
        filterset_class = OrderFilter

# --- 2. INPUT TYPES (Unchanged) ---
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

# --- 3. MUTATIONS (Unchanged) ---
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
        customer = Customer.objects.create(name=input.name, email=input.email, phone=input.phone)
        return CreateCustomer(customer=customer, message="Customer created")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)
    customers = graphene.List(CustomerType) # Note: This returns a simple List, not a Connection
    errors = graphene.List(graphene.String)
    def mutate(root, info, input):
        created = []
        errs = []
        for data in input:
            try:
                if Customer.objects.filter(email=data.email).exists():
                    raise Exception(f"Email {data.email} exists")
                c = Customer.objects.create(name=data.name, email=data.email, phone=data.phone)
                created.append(c)
            except Exception as e:
                errs.append(str(e))
        return BulkCreateCustomers(customers=created, errors=errs)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)
    product = graphene.Field(ProductType)
    def mutate(root, info, input):
        price = Decimal(str(input.price))
        if price <= 0: raise Exception("Price positive")
        p = Product.objects.create(name=input.name, price=price, stock=input.stock)
        return CreateProduct(product=p)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)
    order = graphene.Field(OrderType)
    def mutate(root, info, input):
        # We must decode the Global ID (Relay ID) if passed, but for now assuming standard ID or handling raw
        # Note: In a pure Relay app, IDs are base64 strings.
        # But to keep your previous "ID 1" tests working, we try/except.
        try:
            # Try to get by raw ID first (for existing tests)
            c = Customer.objects.get(pk=input.customer_id)
        except:
             raise Exception("Invalid Customer ID")

        # Handle Products
        products = Product.objects.filter(pk__in=input.product_ids)
        if not products.exists(): raise Exception("No products")
        
        o = Order.objects.create(customer=c)
        o.products.set(products)
        o.total_amount = sum(p.price for p in products)
        o.save()
        return CreateOrder(order=o)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

# --- 4. QUERY (Updated for Filters) ---
class Query(graphene.ObjectType):
    # We explicitly pass filterset_class here to force the connection
    all_customers = DjangoFilterConnectionField(
        CustomerType, 
        filterset_class=CustomerFilter
    )
    all_products = DjangoFilterConnectionField(
        ProductType, 
        filterset_class=ProductFilter
    )
    all_orders = DjangoFilterConnectionField(
        OrderType, 
        filterset_class=OrderFilter
    )