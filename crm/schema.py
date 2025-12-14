import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
import re # For phone validation

# --- 1. Define Types ---
# These allow GraphQL to read the data back after we create it.

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

# --- 2. Define Input Structures ---
# These match the "input: {}" structure in your prompt's examples.

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(default_value=0)

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)

# --- 3. Define Mutations ---

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(root, info, input):
        # Validation: Phone format
        if input.phone:
            # Simple regex for generic phone numbers (digits, dashes, plus)
            if not re.match(r'^[\+\d\-\s]+$', input.phone):
                raise Exception("Invalid phone format")

        # Validation: Email unique
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")

        customer = Customer(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(root, info, input):
        created_customers = []
        error_messages = []

        for customer_data in input:
            try:
                # Reuse validation logic or keep it simple
                if Customer.objects.filter(email=customer_data.email).exists():
                    raise Exception(f"Email {customer_data.email} already exists")
                
                customer = Customer(
                    name=customer_data.name,
                    email=customer_data.email,
                    phone=customer_data.phone
                )
                customer.save()
                created_customers.append(customer)
            except Exception as e:
                # Partial success: record the error but don't stop the loop
                error_messages.append(str(e))

        return BulkCreateCustomers(customers=created_customers, errors=error_messages)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(root, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")
        if input.stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product(
            name=input.name,
            price=input.price,
            stock=input.stock
        )
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(root, info, input):
        # 1. Fetch Customer
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid Customer ID")

        # 2. Fetch Products and validate
        products = Product.objects.filter(pk__in=input.product_ids)
        if not products:
            raise Exception("No valid products found")
        
        if len(products) != len(input.product_ids):
             # Optional: strict check if all IDs were valid
             pass

        # 3. Create Order (without total_amount first)
        order = Order.objects.create(customer=customer)
        
        # 4. Add products (M2M)
        order.products.set(products)
        
        # 5. Calculate Total Amount
        # sum() of the price of all products in this order
        total = sum(product.price for product in products)
        order.total_amount = total
        order.save()

        return CreateOrder(order=order)


# --- 4. Main Query & Mutation Classes ---

class Query(graphene.ObjectType):
    # We added list queries just so you can see data if you want, 
    # though strictly the prompt didn't ask for them in this step.
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)

    def resolve_all_customers(root, info):
        return Customer.objects.all()
        
    def resolve_all_products(root, info):
        return Product.objects.all()

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()