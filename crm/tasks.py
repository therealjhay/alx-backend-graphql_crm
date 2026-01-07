from celery import shared_task
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import requests

@shared_task
def generate_crm_report():
    # 1. Setup GraphQL Client
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        use_json=True,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # 2. Define Query
    # We assume your schema supports fetching all customers and orders with amounts
    # Adjust fields based on your actual schema structure
    query = gql("""
        query {
            allCustomers {
                id
            }
            allOrders {
                id
                totalAmount
            }
        }
    """)

    try:
        result = client.execute(query)
        
        # 3. Process Data
        customers = result.get('allCustomers', [])
        orders = result.get('allOrders', [])
        
        customer_count = len(customers)
        order_count = len(orders)
        
        # Sum revenue (handle potential None values if necessary)
        total_revenue = sum(
            float(order.get('totalAmount') or 0) for order in orders
        )

        # 4. Log Report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = (
            f"{timestamp} - Report: {customer_count} customers, "
            f"{order_count} orders, {total_revenue} revenue\n"
        )
        
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(log_message)

        return "Report generated successfully"

    except Exception as e:
        return f"Error generating report: {e}"