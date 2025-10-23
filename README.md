# mini-crm-repair-requests

sudo pkill -f postgres

# Start
docker compose up -d db

# Run tests
python test_database.py

# Check logs
docker compose logs db

# Stop
docker compose down