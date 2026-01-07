from datetime import datetime

def log_crm_heartbeat():
    # Format the timestamp as requested: DD/MM/YYYY-HH:MM:SS
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    
    # Construct the message
    message = f"{timestamp} CRM is alive\n"
    
    # Append the message to the log file
    try:
        with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
            log_file.write(message)
    except Exception as e:
        # Fallback logging or simple print if file access fails
        print(f"Error logging heartbeat: {e}")