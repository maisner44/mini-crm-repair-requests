# mini-crm-repair-requests

# Start
docker compose up -d db

# Run tests
python test_database.py

# Check logs
docker compose logs db

# Stop
docker compose down