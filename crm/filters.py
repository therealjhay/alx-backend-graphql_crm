import django_filters
from .models import Customer, Product, Order

class CustomerFilter(django_filters.FilterSet):
    # 'icontains' means case-insensitive partial match (e.g., "ali" matches "Alice")
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    
    # Date range filters (gte = greater than/equal, lte = less than/equal)
    created_at_gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    # Challenge: Phone starts with specific pattern
    phone_pattern = django_filters.CharFilter(field_name='phone', lookup_expr='startswith')

    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone']

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    
    # Range filters for price and stock
    price_gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    stock_gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']

class OrderFilter(django_filters.FilterSet):
    total_amount_gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    order_date_gte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='gte')
    order_date_lte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='lte')

    # Nested lookups: Filter order by the related customer's name
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    # Filter by related product's name (distinct ensures no duplicates)
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains', distinct=True)

    class Meta:
        model = Order
        fields = ['total_amount', 'order_date']