from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    # 1. (Optional) Check GraphQL Endpoint Responsiveness
    # We wrap this in a try/except block so the heartbeat log doesn't fail 
    # just because the server is momentarily down or the query fails.
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            use_json=True,
        )
        # Initialize client. We verify connection by attempting a simple query.
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # We query the 'hello' field as suggested in the instructions.
        # Ensure your schema actually has a query named 'hello' or change this field.
        query = gql("""
            query {
                hello
            }
        """)
        client.execute(query)
    except Exception:
        # If connection fails, we pass silently (or you could log the error separately).
        # We proceed to log that the Cron task itself is alive.
        pass

    # 2. Log the Heartbeat
    # Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"
    
    try:
        with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
            log_file.write(message)
    except Exception as e:
        print(f"Error logging heartbeat: {e}")