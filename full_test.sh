#!/bin/bash
set -e

echo "Running Full Application Test Suite"
echo "======================================"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[PASS] $1${NC}"
    else
        echo -e "${RED}[FAIL] $1${NC}"
        exit 1
    fi
}

echo "Testing Health Check..."
curl -s --max-time 5 http://localhost:8000/ | grep -q "Mini-CRM"
check "Health check passed"
echo ""

echo "Testing Admin Login..."
ADMIN_TOKEN=$(curl -s --max-time 5 -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
[ ! -z "$ADMIN_TOKEN" ]
check "Admin login successful"
echo ""

echo "Testing Worker Login..."
WORKER_TOKEN=$(curl -s --max-time 5 -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=worker@example.com&password=worker123" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
[ ! -z "$WORKER_TOKEN" ]
check "Worker login successful"
echo ""

echo "Testing Public Repair Request..."
TICKET_RESPONSE=$(curl -s --max-time 10 -X POST http://localhost:8000/api/v1/public/repair-requests \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test repair request",
    "description": "Testing functionality",
    "client_full_name": "Test User",
    "client_email": "test@example.com",
    "client_phone": "+1234567890"
  }')
echo "$TICKET_RESPONSE" | grep -q "Test repair request"
check "Public request creation works"
TICKET_ID=$(echo "$TICKET_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo ""

echo "Testing Admin Can View All Tickets..."
echo -e "${YELLOW}Requesting tickets list...${NC}"
TICKETS_RESPONSE=$(curl -sL --max-time 10 http://localhost:8000/api/v1/tickets/ \
  -H "Authorization: Bearer $ADMIN_TOKEN")
echo "Response received, checking..."
echo "$TICKETS_RESPONSE" | grep -q "total"
check "Admin can view all tickets"
echo ""

echo "Testing Search Functionality..."
curl -sL --max-time 10 "http://localhost:8000/api/v1/tickets/?search=Test" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | grep -q "Test repair request"
check "Search by title works"
echo ""

echo "Testing Status Filter..."
curl -sL --max-time 10 "http://localhost:8000/api/v1/tickets/?status=new" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | grep -q "new"
check "Status filter works"
echo ""

echo "Testing Pagination..."
curl -sL --max-time 10 "http://localhost:8000/api/v1/tickets/?page=1&page_size=2" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | grep -q "page_size"
check "Pagination works"
echo ""

echo "Testing Worker Assignment..."
WORKER_ID=$(curl -sL --max-time 10 http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | \
  python3 -c "import sys, json; users = json.load(sys.stdin)['items']; print([u['id'] for u in users if u['role'] == 'worker'][0])")

curl -sL --max-time 10 -X POST "http://localhost:8000/api/v1/tickets/$TICKET_ID/assign" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"assigned_to\": \"$WORKER_ID\"}" | grep -q "assigned_to"
check "Admin can assign tickets to workers"
echo ""

echo "Testing Worker Can Update Their Ticket..."
curl -sL --max-time 10 -X PATCH "http://localhost:8000/api/v1/tickets/$TICKET_ID/status" \
  -H "Authorization: Bearer $WORKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}' | grep -q "in_progress"
check "Worker can update their assigned ticket"
echo ""

echo "Testing Worker Permissions..."
HTTP_CODE=$(curl -sL --max-time 10 -w "%{http_code}" -o /dev/null -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer $WORKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"pass","full_name":"Test","role":"worker"}')
[ "$HTTP_CODE" = "403" ]
check "Worker cannot create users (403)"
echo ""

echo "Testing API Documentation..."
curl -s --max-time 10 http://localhost:8000/docs | grep -q "swagger"
check "API documentation accessible"
echo ""

echo "======================================"
echo -e "${GREEN}ALL TESTS PASSED!${NC}"
echo ""
echo "Application URLs:"
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Test Accounts:"
echo "   - Admin: admin@example.com / admin123"
echo "   - Worker: worker@example.com / worker123"