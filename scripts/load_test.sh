#!/bin/bash
# Load test Placement360 backend

# Configuration
HOST="http://localhost:8000"
ENDPOINT="/api/v1/health"
REQUESTS=10000
CONCURRENCY=100

echo "Load Testing Placement360 Backend"
echo "=================================="
echo "Target: ${HOST}${ENDPOINT}"
echo "Requests: ${REQUESTS}"
echo "Concurrency: ${CONCURRENCY}"
echo ""

# Install Apache Bench if needed (Linux)
if ! command -v ab &> /dev/null; then
    echo "Apache Bench not found. Install with:"
    echo "  Ubuntu/Debian: sudo apt-get install apache2-utils"
    echo "  CentOS/RHEL: sudo yum install httpd-tools"
    echo "  macOS: brew install apache-bench"
    exit 1
fi

# Run load test
echo "Starting load test..."
ab -n ${REQUESTS} -c ${CONCURRENCY} -g results.tsv "${HOST}${ENDPOINT}"

echo ""
echo "Load test complete. Results saved to results.tsv"
echo ""
echo "Monitor server during load:"
echo "  curl ${HOST}/api/v1/metrics"
