#!/bin/bash
# Script to test API endpoint coverage for DSPy Docker setup

set -e  # Exit on error

# Text formatting
BOLD="\033[1m"
BLUE="\033[34m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

# Banner
echo -e "${BOLD}${BLUE}DSPy API Endpoint Coverage Test${RESET}"
echo -e "This script tests all API endpoints for 100% coverage.\n"

# Configuration
API_BASE_URL=${1:-"http://localhost:8000"}
QDRANT_HOST=${2:-"localhost"}
MAX_RETRIES=5
RETRY_DELAY=3

# Function to test an endpoint
test_endpoint() {
  local url=$1
  local method=$2
  local name=$3
  local payload=$4
  
  echo -e "Testing ${BOLD}$name${RESET} at $url..."
  
  for ((attempt=1; attempt<=MAX_RETRIES; attempt++)); do
    if [ "$method" = "GET" ]; then
      response=$(curl -s -o response.txt -w "%{http_code}" -X GET "$url" -m 10)
    else
      if [ -n "$payload" ]; then
        response=$(curl -s -o response.txt -w "%{http_code}" -X POST "$url" -H "Content-Type: application/json" -d "$payload" -m 20)
      else
        response=$(curl -s -o response.txt -w "%{http_code}" -X POST "$url" -H "Content-Type: application/json" -d "{}" -m 10)
      fi
    fi
    
    # Check if status code is successful (2xx or 3xx)
    if [ "$response" -lt 400 ]; then
      echo -e "${GREEN}✅ $name check passed with status code $response${RESET}"
      
      # Preview response content for debugging
      if [ -f "response.txt" ]; then
        content_type=$(file -b --mime-type response.txt)
        if [[ "$content_type" == "text/html"* ]]; then
          echo "   Response: HTML content received"
        elif [[ "$content_type" == "application/json" ]]; then
          echo "   Response preview: $(head -c 200 response.txt)..."
        else
          echo "   Response preview: $(head -c 200 response.txt)..."
        fi
      fi
      
      return 0
    else
      if [ $attempt -lt $MAX_RETRIES ]; then
        echo -e "${YELLOW}$name check failed with status code $response (attempt $attempt/$MAX_RETRIES)${RESET}"
        echo -e "Retrying in $RETRY_DELAY seconds..."
        sleep $RETRY_DELAY
      else
        echo -e "${RED}❌ $name check failed with status code $response after all retries${RESET}"
        if [ -f "response.txt" ]; then
          echo -e "   Response: $(head -c 200 response.txt)..."
        fi
        return 1
      fi
    fi
  done
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

echo -e "\n${BOLD}Testing Core API Endpoints:${RESET}"
test_endpoint "$API_BASE_URL/api/v1/status" "GET" "Status API" ""
record_test "Status API" $?

test_endpoint "$API_BASE_URL/api/v1/predict" "POST" "Prediction API" '{"prompt":"What is DSPy?","model":null,"options":{"provider":"nvidia"}}'
record_test "Prediction API" $?

test_endpoint "$API_BASE_URL/api/v1/predict/stream" "POST" "Streaming API" '{"prompt":"Hello","model":null,"options":{"provider":"nvidia"}}'
record_test "Streaming API" $?

test_endpoint "$API_BASE_URL/api/v1/models" "GET" "Available Models" ""
record_test "Available Models" $?

test_endpoint "$API_BASE_URL/api/v1/optimizers" "GET" "Available Optimizers" ""
record_test "Available Optimizers" $?

test_endpoint "$API_BASE_URL/api/v1/modules" "GET" "Available Modules" ""
record_test "Available Modules" $?

echo -e "\n${BOLD}Testing Web Interface Endpoints:${RESET}"
test_endpoint "$API_BASE_URL/" "GET" "Web Interface" ""
record_test "Web Interface" $?

test_endpoint "$API_BASE_URL/dashboard" "GET" "Dashboard" ""
record_test "Dashboard" $?

test_endpoint "$API_BASE_URL/docs" "GET" "API Documentation" ""
record_test "API Documentation" $?

test_endpoint "$API_BASE_URL/openapi.json" "GET" "OpenAPI Schema" ""
record_test "OpenAPI Schema" $?

test_endpoint "$API_BASE_URL/health" "GET" "Health Check" ""
record_test "Health Check" $?

echo -e "\n${BOLD}Testing SAP HANA Vector Store API:${RESET}"
test_endpoint "$API_BASE_URL/api/v1/vectorstore/status" "GET" "Vector Store Status" ""
record_test "Vector Store Status" $?

test_endpoint "$API_BASE_URL/api/v1/vectorstore/collections" "GET" "Vector Store Collections" ""
record_test "Vector Store Collections" $?

# Test a sample vector store query
test_endpoint "$API_BASE_URL/api/v1/vectorstore/search" "POST" "Vector Store Search" '{"query":"test query","k":2}'
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
rm -f response.txt

# Final verdict
if [ "$COVERAGE" -eq 100 ]; then
  echo -e "\n${GREEN}${BOLD}All tests passed! You have 100% API endpoint coverage.${RESET}"
  exit 0
else
  echo -e "\n${RED}${BOLD}Some tests failed. API endpoint coverage is ${COVERAGE}%.${RESET}"
  exit 1
fi