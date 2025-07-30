#!/bin/bash

# XML Generator Workflow Script
# Combines Java Spring Boot application with Python XML generation scripts
# Author: AI Assistant
# Version: 1.0

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPRING_JAR="${SCRIPT_DIR}/spring-ftl/target/spring-ftl-0.0.1-SNAPSHOT.jar"
SPRING_PORT=8080
SPRING_PID_FILE="${SCRIPT_DIR}/spring.pid"
LOG_DIR="${SCRIPT_DIR}/logs"
SPRING_LOG="${LOG_DIR}/spring.log"
PYTHON_LOG="${LOG_DIR}/python.log"
OUTPUT_DIR="${SCRIPT_DIR}/output"
PYTHON_SCRIPTS_DIR="${SCRIPT_DIR}/spring-ftl/src/main/resources/scripts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Cleanup function
cleanup() {
    log "Cleaning up..."
    if [ -f "$SPRING_PID_FILE" ]; then
        SPRING_PID=$(cat "$SPRING_PID_FILE")
        if kill -0 "$SPRING_PID" 2>/dev/null; then
            log "Stopping Spring Boot application (PID: $SPRING_PID)..."
            kill "$SPRING_PID"
            sleep 5
            if kill -0 "$SPRING_PID" 2>/dev/null; then
                warning "Force killing Spring Boot application..."
                kill -9 "$SPRING_PID"
            fi
        fi
        rm -f "$SPRING_PID_FILE"
    fi
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    mkdir -p "$LOG_DIR" "$OUTPUT_DIR"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Java
    if ! command -v java &> /dev/null; then
        error "Java is not installed or not in PATH"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        error "Python is not installed or not in PATH"
        exit 1
    fi
    
    # Set Python command
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
    
    # Check Spring JAR
    if [ ! -f "$SPRING_JAR" ]; then
        error "Spring Boot JAR not found at: $SPRING_JAR"
        log "Building Spring Boot application..."
        cd "${SCRIPT_DIR}/spring-ftl"
        chmod +x mvnw
        ./mvnw clean package -DskipTests
        cd "$SCRIPT_DIR"
        
        if [ ! -f "$SPRING_JAR" ]; then
            error "Failed to build Spring Boot JAR"
            exit 1
        fi
    fi
    
    # Check Python scripts
    if [ ! -d "$PYTHON_SCRIPTS_DIR" ]; then
        error "Python scripts directory not found: $PYTHON_SCRIPTS_DIR"
        exit 1
    fi
    
    success "All prerequisites checked successfully"
}

# Start Spring Boot application
start_spring_boot() {
    log "Starting Spring Boot application..."
    
    # Check if port is already in use
    if netstat -tuln 2>/dev/null | grep -q ":$SPRING_PORT "; then
        warning "Port $SPRING_PORT is already in use. Attempting to stop existing process..."
        pkill -f "spring-ftl" || true
        sleep 3
    fi
    
    # Start Spring Boot in background
    nohup java -jar "$SPRING_JAR" > "$SPRING_LOG" 2>&1 &
    SPRING_PID=$!
    echo $SPRING_PID > "$SPRING_PID_FILE"
    
    log "Spring Boot started with PID: $SPRING_PID"
    log "Waiting for Spring Boot to be ready..."
    
    # Wait for Spring Boot to start (max 60 seconds)
    for i in {1..60}; do
        if curl -f -s "http://localhost:$SPRING_PORT/actuator/health" > /dev/null 2>&1; then
            success "Spring Boot application is ready!"
            return 0
        elif curl -f -s "http://localhost:$SPRING_PORT" > /dev/null 2>&1; then
            success "Spring Boot application is ready!"
            return 0
        fi
        
        if ! kill -0 "$SPRING_PID" 2>/dev/null; then
            error "Spring Boot application failed to start. Check logs: $SPRING_LOG"
            return 1
        fi
        
        sleep 2
        echo -n "."
    done
    
    error "Spring Boot application failed to start within 60 seconds"
    return 1
}

# Run Python XML generation scripts
run_python_scripts() {
    log "Running Python XML generation scripts..."
    
    cd "$PYTHON_SCRIPTS_DIR"
    
    # List of scripts to run in order (from main.py)
    local scripts=(
        "combined.py"
        "mapping.py"
        "lov_impl_.py"
        "screenfinal.py"
    )
    
    # Run main.py which orchestrates all scripts
    if [ -f "main.py" ]; then
        log "Running main.py orchestrator..."
        $PYTHON_CMD main.py 2>&1 | tee -a "$PYTHON_LOG"
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            success "Python scripts executed successfully"
        else
            error "Python scripts execution failed. Check logs: $PYTHON_LOG"
            return 1
        fi
    else
        # Run individual scripts if main.py is not available
        log "Running individual Python scripts..."
        for script in "${scripts[@]}"; do
            if [ -f "$script" ]; then
                log "Running $script..."
                $PYTHON_CMD "$script" 2>&1 | tee -a "$PYTHON_LOG"
                
                if [ ${PIPESTATUS[0]} -ne 0 ]; then
                    error "Failed to run $script"
                    return 1
                fi
            else
                warning "Script $script not found, skipping..."
            fi
        done
        success "All available Python scripts executed"
    fi
    
    cd "$SCRIPT_DIR"
}

# Generate HTTP test files
generate_http_tests() {
    log "Generating HTTP test files..."
    
    if [ -f "${SCRIPT_DIR}/spring-ftl/generate_http_tests.py" ]; then
        cd "${SCRIPT_DIR}/spring-ftl"
        $PYTHON_CMD generate_http_tests.py 2>&1 | tee -a "$PYTHON_LOG"
        cd "$SCRIPT_DIR"
        success "HTTP test files generated"
    else
        warning "HTTP test generator not found, skipping..."
    fi
}

# Copy generated files to output directory
collect_output() {
    log "Collecting generated files..."
    
    # Copy XML files from .idea/demo
    if [ -d ".idea/demo" ]; then
        find .idea/demo -name "*.xml" -exec cp {} "$OUTPUT_DIR/" \; 2>/dev/null || true
    fi
    
    # Copy HTTP test files
    if [ -d "httpRequests" ]; then
        cp -r httpRequests "$OUTPUT_DIR/" 2>/dev/null || true
    fi
    
    # Copy any JSON output files
    find . -name "*.json" -path "*/output/*" -exec cp {} "$OUTPUT_DIR/" \; 2>/dev/null || true
    
    # List generated files
    if [ "$(ls -A "$OUTPUT_DIR" 2>/dev/null)" ]; then
        success "Generated files collected in: $OUTPUT_DIR"
        log "Generated files:"
        ls -la "$OUTPUT_DIR"
    else
        warning "No output files found"
    fi
}

# Git operations
git_operations() {
    if [ "$1" = "--git" ]; then
        log "Performing Git operations..."
        
        # Check if we're in a git repository
        if git rev-parse --git-dir > /dev/null 2>&1; then
            # Pull latest changes
            log "Pulling latest changes..."
            git pull origin main || git pull origin master || true
            
            # Add generated files
            git add "$OUTPUT_DIR" || true
            git add "httpRequests" || true
            git add ".idea/demo" || true
            
            # Commit if there are changes
            if ! git diff --cached --quiet; then
                log "Committing generated files..."
                git commit -m "Auto-generated XML files and HTTP tests - $(date '+%Y-%m-%d %H:%M:%S')"
                
                # Push changes
                log "Pushing changes..."
                git push origin main || git push origin master || true
                success "Git operations completed"
            else
                log "No changes to commit"
            fi
        else
            warning "Not a git repository, skipping git operations"
        fi
    fi
}

# Main execution function
main() {
    log "Starting XML Generator Workflow..."
    log "Script directory: $SCRIPT_DIR"
    
    create_directories
    check_prerequisites
    
    # Start Spring Boot application
    if start_spring_boot; then
        # Run Python scripts
        if run_python_scripts; then
            # Generate HTTP tests
            generate_http_tests
            
            # Collect output
            collect_output
            
            # Git operations if requested
            git_operations "$@"
            
            success "XML Generator Workflow completed successfully!"
        else
            error "Python scripts execution failed"
            exit 1
        fi
    else
        error "Failed to start Spring Boot application"
        exit 1
    fi
}

# Help function
show_help() {
    echo "XML Generator Workflow Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --git       Perform git pull, commit, and push operations"
    echo "  --help      Show this help message"
    echo ""
    echo "This script will:"
    echo "  1. Build and start the Spring Boot application"
    echo "  2. Run Python XML generation scripts"
    echo "  3. Generate HTTP test files"
    echo "  4. Collect all generated files in the output directory"
    echo "  5. Optionally perform git operations"
    echo ""
    echo "Logs are stored in: $LOG_DIR"
    echo "Output files are stored in: $OUTPUT_DIR"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac