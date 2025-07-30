# Spring Boot Application Startup Guide (Linux)

This guide explains how to start the Spring Boot application on Linux systems, replacing the Windows batch file functionality.

## Quick Start

### 1. Start the Application
```bash
./start.sh
```

### 2. Stop the Application
```bash
./stop.sh
```

## What Changed

The original Windows batch file contained Windows-specific commands that don't work on Linux:
- `timeout /t 20 /nobreak` → Replaced with `sleep 20`
- `if %errorlevel% neq 0` → Replaced with proper bash error handling
- `start "SpringBoot"` → Replaced with background process execution using `&`

## Scripts Overview

### start.sh
- **Purpose**: Starts the Spring Boot application on port 8081
- **Features**:
  - Checks Java installation and version
  - Verifies JAR file exists
  - Starts application in background
  - Saves process ID for later management
  - Waits 20 seconds for startup
  - Provides colored output for better readability
  - Creates logs directory automatically

### stop.sh
- **Purpose**: Gracefully stops the running Spring Boot application
- **Features**:
  - Reads process ID from saved file
  - Attempts graceful shutdown (SIGTERM)
  - Waits up to 30 seconds for graceful shutdown
  - Forces termination if needed (SIGKILL)
  - Cleans up PID file

## Prerequisites

1. **Java**: Java 17 or higher must be installed
   ```bash
   java -version
   ```

2. **Built Application**: The Spring Boot JAR must be built
   ```bash
   cd spring-ftl
   ./mvnw clean package -DskipTests
   ```

## File Locations

- **JAR File**: `spring-ftl/target/spring-ftl-0.0.1-SNAPSHOT.jar`
- **PID File**: `spring.pid` (created when application starts)
- **Logs Directory**: `logs/` (created automatically)

## Usage Examples

### Basic Startup
```bash
# Make sure you're in the workspace root directory
./start.sh
```

### Check if Application is Running
```bash
# Check if PID file exists and process is running
if [ -f spring.pid ] && kill -0 $(cat spring.pid) 2>/dev/null; then
    echo "Application is running with PID: $(cat spring.pid)"
else
    echo "Application is not running"
fi
```

### Manual Process Management
```bash
# If you need to manage the process manually:
# Start in background
java -jar spring-ftl/target/spring-ftl-0.0.1-SNAPSHOT.jar --server.port=8081 &

# Save PID
echo $! > spring.pid

# Stop later
kill $(cat spring.pid)
```

## Troubleshooting

### Application Won't Start
1. **Check Java Installation**:
   ```bash
   java -version
   ```

2. **Verify JAR File Exists**:
   ```bash
   ls -la spring-ftl/target/spring-ftl-0.0.1-SNAPSHOT.jar
   ```

3. **Build Application if Missing**:
   ```bash
   cd spring-ftl
   ./mvnw clean package -DskipTests
   cd ..
   ```

### Port Already in Use
If port 8081 is already in use, you can:
1. **Find what's using the port**:
   ```bash
   sudo lsof -i :8081
   ```

2. **Use a different port**:
   ```bash
   java -jar spring-ftl/target/spring-ftl-0.0.1-SNAPSHOT.jar --server.port=8082 &
   ```

### Application Logs
- Application logs are displayed in the terminal when using `./start.sh`
- For background operation, redirect to a log file:
  ```bash
  java -jar spring-ftl/target/spring-ftl-0.0.1-SNAPSHOT.jar --server.port=8081 > logs/spring.log 2>&1 &
  ```

## Access the Application

Once started successfully, the application will be available at:
- **URL**: http://localhost:8081
- **Health Check**: http://localhost:8081/actuator/health (if actuator is enabled)

## Differences from Windows Version

| Windows Command | Linux Equivalent | Purpose |
|----------------|------------------|---------|
| `timeout /t 20 /nobreak` | `sleep 20` | Wait 20 seconds |
| `if %errorlevel% neq 0` | `if [ $? -ne 0 ]` | Check exit code |
| `start "SpringBoot" java -jar...` | `java -jar ... &` | Start in background |
| `pause` | `read -p "Press enter to continue..."` | Wait for user input |

The Linux scripts provide better error handling, colored output, and proper process management compared to the original Windows batch file.