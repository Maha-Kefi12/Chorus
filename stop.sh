#!/bin/bash

# Spring Boot Application Stop Script for Linux

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPRING_PID_FILE="${SCRIPT_DIR}/spring.pid"

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log "Stopping Spring Boot application..."

# Check if PID file exists
if [ ! -f "$SPRING_PID_FILE" ]; then
    warning "PID file not found: $SPRING_PID_FILE"
    warning "Application may not be running or was started manually"
    exit 1
fi

# Read PID from file
SPRING_PID=$(cat "$SPRING_PID_FILE")

# Check if process is running
if ! kill -0 "$SPRING_PID" 2>/dev/null; then
    warning "Process with PID $SPRING_PID is not running"
    rm -f "$SPRING_PID_FILE"
    exit 1
fi

# Gracefully stop the application
log "Sending SIGTERM to process $SPRING_PID..."
kill "$SPRING_PID"

# Wait for graceful shutdown
log "Waiting for application to stop..."
for i in {1..30}; do
    if ! kill -0 "$SPRING_PID" 2>/dev/null; then
        success "Application stopped successfully"
        rm -f "$SPRING_PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill if graceful shutdown failed
warning "Graceful shutdown failed, forcing termination..."
kill -9 "$SPRING_PID" 2>/dev/null || true
rm -f "$SPRING_PID_FILE"
success "Application forcefully terminated"