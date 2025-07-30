# Spring Boot Application Startup Guide (Windows)

This guide explains how to properly start the Spring Boot application on Windows systems.

## Quick Start

### Option 1: Full Application with XML Generator
```cmd
start.bat
```

### Option 2: Spring Boot Only
```cmd
start-spring-only.bat
```

## What Was Wrong Before

The issue you experienced was that the batch file was being executed line by line in the command prompt instead of running as a complete script. This happened because:

1. **Missing `@echo off`**: Without this, each command was displayed before execution
2. **Improper script structure**: The commands weren't properly grouped in a batch file
3. **Missing error handling**: No proper checks for Java installation or file existence

## Files Provided

### `start.bat` (Full Version)
- ✅ Checks Java installation
- ✅ Displays Java version
- ✅ Validates JAR file existence
- ✅ Starts Spring Boot application on port 8081
- ✅ Waits 20 seconds for startup
- ✅ Runs XML generator if available
- ✅ Provides clear status messages
- ✅ Proper error handling

### `start-spring-only.bat` (Simple Version)
- ✅ Basic Java check
- ✅ Starts Spring Boot application only
- ✅ 20-second wait period
- ✅ Simple and straightforward

## Prerequisites

1. **Java Installation**: Java 17 or higher must be installed and in PATH
2. **JAR File**: You need either:
   - `spring-ftl.jar` in the current directory, OR
   - Built JAR at `spring-ftl\target\spring-ftl-0.0.1-SNAPSHOT.jar`

## Step-by-Step Usage

### 1. Prepare the Environment
```cmd
# Navigate to your application directory
cd "C:\Users\USER\Downloads\application-windows-x64 (1)"

# Ensure you have the JAR file
dir spring-ftl.jar
```

### 2. Run the Startup Script
```cmd
# Double-click start.bat in Windows Explorer
# OR run from command prompt:
start.bat
```

### 3. Verify Application is Running
- Wait for the "Application Started Successfully!" message
- Open browser and go to: http://localhost:8081
- You should see the Spring Boot application

## Troubleshooting

### Problem: "Java is not installed or not in PATH"
**Solution:**
1. Install Java 17 or higher from [Oracle](https://www.oracle.com/java/technologies/downloads/) or [OpenJDK](https://openjdk.org/)
2. Add Java to your PATH environment variable
3. Test with: `java -version`

### Problem: "Spring Boot JAR file not found"
**Solutions:**
1. **If you have the built JAR:**
   ```cmd
   copy "spring-ftl\target\spring-ftl-0.0.1-SNAPSHOT.jar" "spring-ftl.jar"
   ```

2. **If you need to build it:**
   ```cmd
   cd spring-ftl
   mvnw.cmd clean package -DskipTests
   cd ..
   copy "spring-ftl\target\spring-ftl-0.0.1-SNAPSHOT.jar" "spring-ftl.jar"
   ```

### Problem: Port 8081 already in use
**Solutions:**
1. **Find what's using the port:**
   ```cmd
   netstat -ano | findstr :8081
   ```

2. **Kill the process (replace PID with actual process ID):**
   ```cmd
   taskkill /PID <PID> /F
   ```

3. **Use a different port:**
   - Edit the batch file and change `--server.port=8081` to `--server.port=8082`

### Problem: Application starts but can't access it
**Check:**
1. Wait the full 20 seconds for startup
2. Check Windows Firewall isn't blocking Java
3. Try: http://127.0.0.1:8081 instead of localhost
4. Look for error messages in the Spring Boot window

## Manual Commands (if batch files don't work)

If the batch files still don't work, you can run these commands manually:

```cmd
# Check Java
java -version

# Start Spring Boot (this will run in the foreground)
java -jar spring-ftl.jar --server.port=8081

# OR start in background (new window)
start "SpringBoot" java -jar spring-ftl.jar --server.port=8081
```

## Stopping the Application

### Method 1: Close the Spring Boot Window
- Find the "Spring Boot Application" window that opened
- Click the X button or press Ctrl+C

### Method 2: Task Manager
1. Open Task Manager (Ctrl+Shift+Esc)
2. Find "java.exe" process
3. Right-click → End Task

### Method 3: Command Line
```cmd
# Find Java processes
tasklist | findstr java

# Kill specific process (replace PID)
taskkill /PID <PID> /F
```

## File Structure Expected

```
C:\Users\USER\Downloads\application-windows-x64 (1)\
├── start.bat                    (Full startup script)
├── start-spring-only.bat        (Simple startup script)
├── spring-ftl.jar              (Spring Boot application)
├── xml-generator.exe           (Optional XML generator)
└── spring-ftl\                 (Source code directory)
    └── target\
        └── spring-ftl-0.0.1-SNAPSHOT.jar
```

## Success Indicators

When everything works correctly, you should see:
1. ✅ Java version displayed
2. ✅ "Starting Spring Boot application on port 8081..."
3. ✅ New window opens with Spring Boot logs
4. ✅ "Application Started Successfully!" message
5. ✅ Access to http://localhost:8081 works

The key difference from your previous experience is that now the batch file will run as a complete script instead of executing each line individually in the command prompt.