#!/bin/bash
# Script to test local API endpoints for DSPy without Docker

set -e  # Exit on error

# Text formatting
BOLD="\033[1m"
BLUE="\033[34m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

# Banner
echo -e "${BOLD}${BLUE}DSPy Local API Endpoint Test${RESET}"
echo -e "This script tests the DSPy API endpoints running locally.\n"

# Configuration
API_BASE_URL=${1:-"http://localhost:8000"}
TEST_PORT=8000  # Use the default port for the test server

# Check if the mock API server file exists
if [ ! -f "scripts/local_api_test.py" ]; then
    echo -e "${RED}Error: scripts/local_api_test.py not found${RESET}"
    exit 1
fi

# Check if the necessary Python packages are installed
echo -e "${BOLD}Checking Python packages...${RESET}"
python3 -c "import fastapi, uvicorn, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}FastAPI or dependencies not found. Installing...${RESET}"
    pip install fastapi uvicorn pydantic
fi

# Start the mock API server
echo -e "\n${BOLD}Starting mock API server on port ${TEST_PORT}...${RESET}"
python3 scripts/local_api_test.py --port ${TEST_PORT} &
SERVER_PID=$!

# Wait for server to start
echo -e "Waiting for server to initialize..."
sleep 3

# Function to test an endpoint
test_endpoint() {
    local url=$1
    local method=$2
    local name=$3
    local payload=$4
    
    echo -e "Testing ${BOLD}$name${RESET} at $url..."
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -o response.txt -w "%{http_code}" -X GET "$url" -m 10)
    else
        if [ -n "$payload" ]; then
            response=$(curl -s -o response.txt -w "%{http_code}" -X POST "$url" -H "Content-Type: application/json" -d "$payload" -m 10)
        else
            response=$(curl -s -o response.txt -w "%{http_code}" -X POST "$url" -H "Content-Type: application/json" -d "{}" -m 10)
        fi
    fi
    
    # Check if status code is successful (2xx or 3xx)
    if [ "$response" -lt 400 ]; then
        echo -e "${GREEN}✅ $name check passed with status code $response${RESET}"
        return 0
    else
        echo -e "${RED}❌ $name check failed with status code $response${RESET}"
        if [ -f "response.txt" ]; then
            echo -e "   Response: $(head -c 200 response.txt)..."
        fi
        return 1
    fi
}

# Test results array
declare -a TEST_RESULTS
declare -a TEST_NAMES

# Function to record test result
record_test() {
    local name=$1
    local result=$2
    TEST_NAMES+=("$name")
    TEST_RESULTS+=($result)
}

# Run tests
echo -e "\n${BOLD}Testing Core API Endpoints:${RESET}"
test_endpoint "http://localhost:${TEST_PORT}/api/v1/status" "GET" "Status API" ""
record_test "Status API" $?

test_endpoint "http://localhost:${TEST_PORT}/api/v1/predict" "POST" "Prediction API" '{"prompt":"What is DSPy?","model":null,"options":{"provider":"nvidia"}}'
record_test "Prediction API" $?

test_endpoint "http://localhost:${TEST_PORT}/api/v1/models" "GET" "Available Models" ""
record_test "Available Models" $?

test_endpoint "http://localhost:${TEST_PORT}/api/v1/optimizers" "GET" "Available Optimizers" ""
record_test "Available Optimizers" $?

test_endpoint "http://localhost:${TEST_PORT}/api/v1/modules" "GET" "Available Modules" ""
record_test "Available Modules" $?

echo -e "\n${BOLD}Testing Web Interface Endpoints:${RESET}"
test_endpoint "http://localhost:${TEST_PORT}/" "GET" "Web Interface" ""
record_test "Web Interface" $?

test_endpoint "http://localhost:${TEST_PORT}/health" "GET" "Health Check" ""
record_test "Health Check" $?

test_endpoint "http://localhost:${TEST_PORT}/openapi.json" "GET" "OpenAPI Schema" ""
record_test "OpenAPI Schema" $?

echo -e "\n${BOLD}Testing SAP HANA Vector Store API:${RESET}"
test_endpoint "http://localhost:${TEST_PORT}/api/v1/vectorstore/status" "GET" "Vector Store Status" ""
record_test "Vector Store Status" $?

test_endpoint "http://localhost:${TEST_PORT}/api/v1/vectorstore/collections" "GET" "Vector Store Collections" ""
record_test "Vector Store Collections" $?

test_endpoint "http://localhost:${TEST_PORT}/api/v1/vectorstore/search" "POST" "Vector Store Search" '{"query":"test query","k":2}'
record_test "Vector Store Search" $?

# Calculate coverage
TOTAL_TESTS=${#TEST_RESULTS[@]}
PASSED_TESTS=0

for result in "${TEST_RESULTS[@]}"; do
    if [ "$result" -eq 0 ]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
    fi
done

COVERAGE=$((PASSED_TESTS * 100 / TOTAL_TESTS))

# Print test results summary
echo -e "\n${BOLD}Test Results Summary:${RESET}"
echo -e "Total endpoints tested: $TOTAL_TESTS"
echo -e "Endpoints passed: $PASSED_TESTS"
echo -e "Coverage: ${COVERAGE}%"

# Print detailed results
echo -e "\n${BOLD}Detailed Results:${RESET}"
for i in "${!TEST_NAMES[@]}"; do
    if [ "${TEST_RESULTS[$i]}" -eq 0 ]; then
        echo -e "${GREEN}✅ ${TEST_NAMES[$i]}${RESET}"
    else
        echo -e "${RED}❌ ${TEST_NAMES[$i]}${RESET}"
    fi
done

# Clean up
echo -e "\n${BOLD}Cleaning up...${RESET}"
kill $SERVER_PID
rm -f response.txt

# Final verdict
if [ "$COVERAGE" -eq 100 ]; then
    echo -e "\n${GREEN}${BOLD}All tests passed! You have 100% API endpoint coverage.${RESET}"
    exit 0
else
    echo -e "\n${RED}${BOLD}Some tests failed. API endpoint coverage is ${COVERAGE}%.${RESET}"
    exit 1
fi