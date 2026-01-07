#!/bin/bash

# Define the Python code to run
# We use a 'Here-Doc' (<< EOM) to pass multiple lines of Python cleanly
read -r -d '' PYTHON_SCRIPT << EOM
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer  # Ensure this import matches your project structure

# Calculate the cutoff date (1 year ago)
one_year_ago = timezone.now() - timedelta(days=365)

# Identify customers who do NOT have any orders created after the cutoff date
# This covers customers with old orders OR no orders at all.
inactive_customers = Customer.objects.exclude(orders__created_at__gte=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()

print(f"Deleted {count} inactive customers.")
EOM

# Run the python code using Django's shell
# We capture the output into a variable
OUTPUT=$(echo "$PYTHON_SCRIPT" | python3 manage.py shell)

# Log the timestamp and the output to the specified log file
echo "$(date): $OUTPUT" >> /tmp/customer_cleanup_log.txt