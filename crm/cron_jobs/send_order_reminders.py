import os
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def send_reminders():
    # 1. Setup the GraphQL Client
    # We point it to the localhost endpoint where Django is running
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        use_json=True,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # 2. Define the Query
    # We fetch ID, Customer Email, and Order Date.
    # Note: Ensure these field names match your specific schema.
    query = gql("""
        query {
            allOrders {
                id
                orderDate
                customer {
                    email
                }
            }
        }
    """)

    try:
        # Execute the query
        response = client.execute(query)
        orders = response.get("allOrders", [])

        # 3. Filter for orders within the last 7 days
        # We assume orderDate comes back as an ISO string (e.g., "2023-10-05")
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        reminders_sent = 0

        # Open the log file in append mode
        with open("/tmp/order_reminders_log.txt", "a") as log_file:
            for order in orders:
                # Parse the date string from GraphQL (adjust format if your API differs)
                # Assuming YYYY-MM-DD or ISO format
                try:
                    order_date_str = order.get("orderDate")
                    # flexible parsing for date or datetime string
                    order_date = datetime.fromisoformat(str(order_date_str).replace('Z', '+00:00')).date() if 'T' in str(order_date_str) else datetime.strptime(str(order_date_str), "%Y-%m-%d").date()
                    
                    # Check if date is within range
                    if order_date >= seven_days_ago.date():
                        customer_email = order.get("customer", {}).get("email", "Unknown")
                        order_id = order.get("id")
                        
                        # Log the entry
                        log_entry = f"{datetime.now().isoformat()} - Reminder for Order #{order_id} sent to {customer_email}\n"
                        log_file.write(log_entry)
                        reminders_sent += 1
                        
                except (ValueError, TypeError) as e:
                    # Handle date parsing errors gracefully
                    continue

        # 4. Print required console output
        print("Order reminders processed!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    send_reminders()