# mini-crm-repair-requests

## Quick Start Guide

### 1. Stop System PostgreSQL (if running)
```bash
sudo pkill -f postgres
```

### 2. Start Docker PostgreSQL
```bash
docker compose up -d db
```

### 3. Test Database Models
```bash
python test_database.py
```

### 4. Test Authentication
```bash
python test_auth.py
```

### 5. Start FastAPI Server (Terminal 1)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 6. Test API Endpoints (Terminal 2)
```bash
# In a new terminal
source venv/bin/activate
python test_api.py
```

### 7. Interactive API Documentation
Open in browser while server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Useful Commands

```bash
# Check logs
docker compose logs db

# Check running containers
docker compose ps

# Stop
docker compose down

# Stop and remove all data
docker compose down -v

# Restart fresh
docker compose down -v && docker compose up -d db
```

## API Endpoints

### Public (No Auth Required)
- `POST /api/v1/public/repair-requests` - Create repair request

### Authentication
- `POST /api/v1/auth/login` - Login (returns JWT token)

### Users (Admin Only)
- `GET /api/v1/users` - List all users (paginated)
- `POST /api/v1/users` - Create new user
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Tickets (Admin & Worker)
- `GET /api/v1/tickets` - List tickets (admin sees all, worker sees assigned)
- `GET /api/v1/tickets/{id}` - Get ticket details
- `POST /api/v1/tickets/{id}/assign` - Assign ticket to worker (admin only)
- `PATCH /api/v1/tickets/{id}/status` - Update ticket status

## Test Credentials

After running `test_api.py`, these users are available:
- **Admin**: admin@test.com / admin123
- **Worker**: worker@test.com / worker123