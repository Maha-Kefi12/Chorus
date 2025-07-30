#!/bin/bash

# Spring Boot Application Startup Script for Linux
# This script replaces the Windows batch file functionality

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPRING_JAR="${SCRIPT_DIR}/spring-ftl/target/spring-ftl-0.0.1-SNAPSHOT.jar"
SPRING_PORT=8081
LOG_DIR="${SCRIPT_DIR}/logs"
SPRING_LOG="${LOG_DIR}/spring.log"

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

# Check Java installation
log "Checking Java installation..."
if ! command -v java &> /dev/null; then
    error "Java is not installed or not in PATH"
    error "Please install Java 17 or higher to run this application"
    exit 1
fi

# Display Java version
java -version

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

echo
log "Starting Spring Boot application on port $SPRING_PORT..."

# Check if JAR file exists
if [ ! -f "$SPRING_JAR" ]; then
    error "Spring Boot JAR file not found: $SPRING_JAR"
    error "Please build the application first by running: cd spring-ftl && ./mvnw clean package -DskipTests"
    exit 1
fi

# Start the Spring Boot application
log "Starting application..."
java -jar "$SPRING_JAR" --server.port="$SPRING_PORT" &
SPRING_PID=$!

# Save PID for later use
echo $SPRING_PID > "${SCRIPT_DIR}/spring.pid"

log "Application started with PID: $SPRING_PID"
log "Waiting 20 seconds for application to start..."

# Wait for application to start (equivalent to timeout /t 20 /nobreak)
sleep 20

# Check if the application is still running
if kill -0 $SPRING_PID 2>/dev/null; then
    success "Spring Boot application is running successfully!"
    success "Application URL: http://localhost:$SPRING_PORT"
    success "Process ID: $SPRING_PID"
    success "Logs are being written to: $SPRING_LOG"
    echo
    log "To stop the application, run: kill $SPRING_PID"
    log "Or use the stop script if available"
else
    error "Application failed to start. Check the logs for details."
    exit 1
fi