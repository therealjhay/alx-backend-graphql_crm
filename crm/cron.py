from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# ... (keep your existing log_crm_heartbeat function here) ...

def update_low_stock():
    # 1. Setup Client
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        use_json=True,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # 2. Define the Mutation
    # We request the 'name' and new 'stock' to use in our log
    mutation = gql("""
        mutation {
            updateLowStockProducts {
                success
                updatedProducts {
                    name
                    stock
                }
            }
        }
    """)

    try:
        # 3. Execute Mutation
        result = client.execute(mutation)
        data = result.get('updateLowStockProducts', {})
        
        updated_products = data.get('updatedProducts', [])
        
        # 4. Log Updates
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            if not updated_products:
                log_file.write(f"{timestamp} - No low stock products found.\n")
            else:
                for prod in updated_products:
                    log_entry = f"{timestamp} - Restocked: {prod['name']} -> New Stock: {prod['stock']}\n"
                    log_file.write(log_entry)
                    
    except Exception as e:
        print(f"Error running stock update cron: {e}")