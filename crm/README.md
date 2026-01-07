# CRM Background Tasks Setup

This project uses Celery and Redis to handle background reporting tasks.

## Prerequisites
1. **Redis Server**: Ensure Redis is installed and running.
   - Ubuntu: `sudo apt install redis-server`
   - Mac: `brew install redis`
   - Start: `redis-server`

2. **Python Dependencies**:
   ```bash
   pip install -r requirements.txt

   setup steps