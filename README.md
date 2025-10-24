# Mini-CRM Repair Requests

A FastAPI-based repair request management system with role-based access control.

## Features

- Public API for submitting repair requests
- JWT-based authentication
- Role-based access control (Admin, Worker)
- User management (CRUD operations)
- Ticket assignment and status tracking
- Search and filtering capabilities
- Pagination on all list endpoints

## Tech Stack

- Python 3.13+
- FastAPI
- Pydantic 2.0+
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Alembic
- Docker & Docker Compose

## Docker Hub

Image: `maisner44/mini-crm-repair-requests:latest`

### For Developers: Run from Docker Hub

**One-Command Setup (Recommended):**

```bash
curl -O https://raw.githubusercontent.com/maisner44/mini-crm-repair-requests/main/docker-compose.prod.yml && docker compose -f docker-compose.prod.yml up -d && sleep 15 && docker compose -f docker-compose.prod.yml exec app python scripts/seed.py
```

**What this does:**
1. Downloads the production docker-compose configuration
2. Pulls and starts the application from Docker Hub
3. Automatically runs database migrations on startup
4. Waits for initialization (15 seconds)
5. Seeds admin and worker test accounts

**Access the application:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Test accounts:**
- Admin: `admin@example.com` / `admin123`
- Worker: `worker@example.com` / `worker123`

**To stop:**
```bash
docker compose -f docker-compose.prod.yml down
```

**To stop and remove all data:**
```bash
docker compose -f docker-compose.prod.yml down -v
```

Follow these steps to get the application running from a fresh start:

#### 1. Clone the Repository

```bash
git clone https://github.com/maisner44/mini-crm-repair-requests.git
cd mini-crm-repair-requests
```

#### 2. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your settings (optional for local development)
# The default values work out of the box
```

#### 3. Start the Application

```bash
# Build and start all services (database + application)
docker compose up -d

# Check if services are running
docker compose ps
```

Expected output:
```
NAME                IMAGE                                    STATUS
mini_crm_app        mini-crm-repair-requests-app             Up
mini_crm_db         postgres:16-alpine                       Up (healthy)
```

#### 4. Wait for Application to Initialize

```bash
# Wait for migrations to complete
sleep 10

# Check application logs
docker compose logs app | tail -20
```

Expected logs:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 75a15de5aba0, Create all tables
INFO:     Started server process [1]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 5. Create Test Accounts

```bash
# Seed the database with admin and worker accounts
docker compose exec app python scripts/seed.py
```

Expected output:
```
Database seeded successfully:
  - Admin: admin@example.com / admin123
  - Worker: worker@example.com / worker123
```

#### 6. Verify Installation

```bash
# Test the API health endpoint
curl http://localhost:8000/

# Expected response:
# {"message":"Mini-CRM Repair Requests API"}
```

#### 7. Access the Application

- **API Base URL**: `http://localhost:8000`
- **Interactive Documentation**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

### Stopping the Application

```bash
# Stop containers (keeps data)
docker compose down

# Stop and remove all data (complete cleanup)
docker compose down -v

# Just pause containers (faster restart)
docker compose stop
```

### Restarting the Application

```bash
# If stopped with 'docker compose stop'
docker compose start

# If removed with 'docker compose down'
docker compose up -d

# Full restart
docker compose restart
```

### Troubleshooting

#### Database Connection Issues

```bash
# Check database status
docker compose ps db

# View database logs
docker compose logs db

# Restart database
docker compose restart db
```

#### Application Won't Start

```bash
# Check application logs
docker compose logs app

# Rebuild and restart
docker compose down
docker compose up -d --build

# Check if port 8000 is already in use
lsof -i :8000  # On Linux/Mac
netstat -ano | findstr :8000  # On Windows
```

#### Migrations Not Running

```bash
# Check if migrations ran on startup
docker compose logs app | grep alembic

# Manually run migrations if needed
docker compose exec app alembic upgrade head
```

#### Reset Everything

```bash
# Complete cleanup and fresh start
docker compose down -v
docker system prune -f
docker compose up -d
sleep 10
docker compose exec app python scripts/seed.py
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/mini_crm
DATABASE_URL_SYNC=postgresql://postgres:postgres@db:5432/mini_crm
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=False
```

### Database Migrations

Migrations are **automatically applied** when the container starts (configured in Dockerfile CMD).

To manually run migrations:
```bash
docker compose exec app alembic upgrade head
```

To create a new migration:
```bash
docker compose exec app alembic revision --autogenerate -m "Description"
```

To view migration history:
```bash
docker compose exec app alembic history
```

### Test Accounts

**Admin Account:**
- Email: `admin@example.com`
- Password: `admin123`
- Permissions: Full access to all endpoints

**Worker Account:**
- Email: `worker@example.com`
- Password: `worker123`
- Permissions: View and update assigned tickets only

## API Endpoints

### Public Endpoints

- `POST /api/v1/public/repair-requests` - Submit a repair request

### Authentication

- `POST /api/v1/auth/login` - Login (returns JWT token)

### Users (Admin only)

- `GET /api/v1/users` - List users (paginated)
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Tickets

- `GET /api/v1/tickets` - List tickets (paginated, filtered)
  - Query params: `page`, `page_size`, `status`, `search`
- `GET /api/v1/tickets/{ticket_id}` - Get ticket details
- `POST /api/v1/tickets/{ticket_id}/assign` - Assign ticket to worker (Admin only)
- `PATCH /api/v1/tickets/{ticket_id}/status` - Update ticket status

### Interactive API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

### Complete Testing Guide

Follow these steps to run all tests from scratch:

#### Prerequisites for Testing

```bash
# Ensure the application is running
docker compose up -d

# Wait for services to be ready
sleep 10

# Verify application is accessible
curl http://localhost:8000/
```

#### Method 1: Integration Tests (Recommended for Quick Validation)

**Full end-to-end testing with bash script:**

```bash
# Make sure application is running
docker compose up -d

# Seed test accounts if not already done
docker compose exec app python scripts/seed.py

# Run comprehensive integration tests
bash full_test.sh
```

**What the integration test validates:**

1. Health check endpoint
2. Admin authentication with JWT
3. Worker authentication with JWT
4. Public repair request submission (no auth required)
5. Admin can view all tickets with pagination
6. Search functionality by title
7. Status filtering
8. Pagination parameters
9. Admin can assign tickets to workers
10. Worker can update status of assigned tickets
11. Role-based access control (Worker cannot create users - 403)
12. API documentation accessibility

**Expected output:**
```
Running Full Application Test Suite
======================================

[1/12] Testing Health Check...
[PASS] Health check passed

[2/12] Testing Admin Login...
[PASS] Admin login successful

[3/12] Testing Worker Login...
[PASS] Worker login successful

[4/12] Testing Public Repair Request...
[PASS] Public request creation works

[5/12] Testing Admin Can View All Tickets...
[PASS] Admin can view all tickets

[6/12] Testing Search Functionality...
[PASS] Search by title works

[7/12] Testing Status Filter...
[PASS] Status filter works

[8/12] Testing Pagination...
[PASS] Pagination works

[9/12] Testing Worker Assignment...
[PASS] Admin can assign tickets to workers

[10/12] Testing Worker Can Update Their Ticket...
[PASS] Worker can update their assigned ticket

[11/12] Testing Worker Permissions...
[PASS] Worker cannot create users (403)

[12/12] Testing API Documentation...
[PASS] API documentation accessible

======================================
ALL TESTS PASSED!
```

#### Method 2: Unit and Integration Tests with pytest

**Setup for pytest:**

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows

# Install test dependencies
pip install pytest pytest-asyncio httpx pytest-cov

# Or install all dependencies
pip install -r requirements.txt
```

**Run all tests:**

```bash
# Run all test files with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html  # On Mac
xdg-open htmlcov/index.html  # On Linux
start htmlcov/index.html  # On Windows
```

**Run specific test categories:**

```bash
# Test authentication system only
pytest tests/test_auth.py -v

# Test API endpoints only
pytest tests/test_api.py -v

# Test database models only
pytest tests/test_database.py -v
```

**Pytest output example:**
```
tests/test_auth.py::test_login_success PASSED
tests/test_auth.py::test_login_invalid_credentials PASSED
tests/test_auth.py::test_token_validation PASSED
tests/test_api.py::test_create_repair_request PASSED
tests/test_api.py::test_list_tickets PASSED
tests/test_database.py::test_user_model PASSED
tests/test_database.py::test_ticket_model PASSED

============= 12 passed in 5.23s =============
```

#### Method 3: Individual Test Scripts

**Run standalone test scripts:**

```bash
# Test authentication system
python tests/test_auth.py

# Test API endpoints (requires running server)
python tests/test_api.py

# Test database models
python tests/test_database.py
```

#### Method 4: Manual Testing with curl

**Step-by-step manual API testing:**

```bash
# 1. Health check
curl http://localhost:8000/

# 2. Login as admin and get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"

# Save the token from response
export TOKEN="<paste-your-token-here>"

# 3. Submit public repair request (no auth required)
curl -X POST http://localhost:8000/api/v1/public/repair-requests \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Laptop screen repair",
    "description": "Screen is cracked",
    "client_full_name": "John Doe",
    "client_email": "john@example.com",
    "client_phone": "+1234567890"
  }'

# 4. List all tickets (requires admin token)
curl http://localhost:8000/api/v1/tickets/ \
  -H "Authorization: Bearer $TOKEN"

# 5. Search tickets by title
curl "http://localhost:8000/api/v1/tickets/?search=laptop" \
  -H "Authorization: Bearer $TOKEN"

# 6. Filter tickets by status
curl "http://localhost:8000/api/v1/tickets/?status=new" \
  -H "Authorization: Bearer $TOKEN"

# 7. List users (admin only)
curl http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN"
```

#### Method 5: Interactive Testing with Swagger UI

**Using the built-in API documentation:**

1. **Start the application:**
   ```bash
   docker compose up -d
   ```

2. **Open Swagger UI in browser:**
   ```
   http://localhost:8000/docs
   ```

3. **Authenticate:**
   - Click the green "Authorize" button at the top
   - Enter credentials:
     - Username: `admin@example.com`
     - Password: `admin123`
   - Click "Authorize"
   - Click "Close"

4. **Test endpoints interactively:**
   - Expand any endpoint
   - Click "Try it out"
   - Fill in parameters
   - Click "Execute"
   - View the response

5. **Test different roles:**
   - Log out and authenticate as worker
   - Username: `worker@example.com`
   - Password: `worker123`
   - Try accessing admin-only endpoints (should get 403)

### Testing Checklist

Use this checklist to validate all functionality:

- [ ] Application starts successfully with `docker compose up -d`
- [ ] Health check returns API information
- [ ] Admin can login and receive JWT token
- [ ] Worker can login and receive JWT token
- [ ] Invalid credentials return 401 error
- [ ] Public repair request submission works without authentication
- [ ] Admin can view all tickets
- [ ] Worker can view only assigned tickets
- [ ] Search by title returns correct results
- [ ] Status filtering works
- [ ] Pagination works with page and page_size parameters
- [ ] Admin can create new users
- [ ] Admin can assign tickets to workers
- [ ] Worker can update status of assigned tickets
- [ ] Worker cannot update tickets not assigned to them (403)
- [ ] Worker cannot create users (403)
- [ ] Worker cannot delete users (403)
- [ ] Swagger UI documentation is accessible
- [ ] ReDoc documentation is accessible

### Test Accounts

Use these credentials for testing:

**Admin Account:**
- Email: `admin@example.com`
- Password: `admin123`
- Permissions: 
  - Full access to all endpoints
  - Can create, read, update, delete users
  - Can assign tickets to workers
  - Can view all tickets

**Worker Account:**
- Email: `worker@example.com`
- Password: `worker123`
- Permissions:
  - Can view tickets assigned to them
  - Can update status of assigned tickets
  - Cannot access admin endpoints
  - Cannot modify other workers' tickets

### Continuous Testing During Development

**Run tests automatically on file changes:**

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on any file change
ptw tests/ -- -v
```

**Quick test cycle:**

```bash
# Make code changes
# Run quick integration test
bash full_test.sh

# If passed, run full test suite
pytest tests/ -v
```

## Development

### Local Development Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start PostgreSQL:
```bash
docker compose up -d db
```

4. Run migrations:
```bash
alembic upgrade head
```

5. Seed data:
```bash
python scripts/seed.py
```

6. Run development server:
```bash
uvicorn app.main:app --reload
```

### Development with Docker

```bash
# Build and run in development mode
docker compose up --build

# View logs in real-time
docker compose logs -f app

# Execute commands in running container
docker compose exec app python scripts/seed.py
docker compose exec app alembic upgrade head

# Access database directly
docker compose exec db psql -U postgres -d mini_crm
```

## CI/CD

The project uses GitHub Actions for automated builds and deployments.

On push to `main` or on tags:
- Runs automated tests
- Builds Docker image
- Pushes to Docker Hub with appropriate tags