# XML Generator Workflow System

## Overview

This system combines a Java Spring Boot application with Python scripts to generate XML files from Java class analysis. The workflow includes:

1. **Java Spring Boot Application**: Analyzes Java classes and provides REST APIs
2. **Python Scripts**: Generate XML configurations based on the analysis
3. **Automated Workflow**: Orchestrates the entire process with proper error handling
4. **Git Integration**: Automatically commits and pushes generated files

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Java Classes  │───▶│  Spring Boot App │───▶│  REST APIs      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   XML Files     │◀───│  Python Scripts │◀───│  HTTP Requests  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Files Structure

```
project/
├── spring-ftl/                          # Spring Boot application
│   ├── src/main/java/                   # Java source code
│   ├── src/main/resources/scripts/      # Python scripts
│   │   ├── main.py                      # Main orchestrator
│   │   ├── combined.py                  # XML generation
│   │   ├── mapping.py                   # Field mapping
│   │   ├── lov_impl_.py                 # LOV implementation
│   │   └── screenfinal.py               # Screen configuration
│   ├── target/spring-ftl-*.jar          # Built JAR file
│   └── generate_http_tests.py           # HTTP test generator
├── run-xml-generator.sh                 # Linux/macOS workflow script
├── run-xml-generator.bat                # Windows workflow script
├── main.spec                            # PyInstaller specification
├── output/                              # Generated files directory
├── logs/                                # Log files directory
└── .github/workflows/                   # CI/CD workflows
```

## Usage

### Prerequisites

- **Java 17+**: For running the Spring Boot application
- **Python 3.8+**: For running the generation scripts
- **Maven**: For building the Spring Boot application (optional, uses wrapper)
- **Git**: For version control operations (optional)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Run the workflow**:
   
   **Linux/macOS**:
   ```bash
   ./run-xml-generator.sh
   ```
   
   **Windows**:
   ```cmd
   run-xml-generator.bat
   ```

3. **With Git operations**:
   ```bash
   ./run-xml-generator.sh --git
   ```

### Advanced Usage

#### Manual Steps

1. **Build Spring Boot application**:
   ```bash
   cd spring-ftl
   ./mvnw clean package -DskipTests
   ```

2. **Start Spring Boot application**:
   ```bash
   java -jar spring-ftl/target/spring-ftl-0.0.1-SNAPSHOT.jar
   ```

3. **Run Python scripts**:
   ```bash
   cd spring-ftl/src/main/resources/scripts
   python main.py
   ```

4. **Generate HTTP tests**:
   ```bash
   cd spring-ftl
   python generate_http_tests.py
   ```

#### Using the REST API

The Spring Boot application provides several endpoints:

- `GET /api/analyze?path=<java-file-path>`: Analyze Java class
- `GET /api/extract-function?path=<java-file-path>`: Extract function name
- Additional endpoints for field analysis and XML generation

Example:
```bash
curl "http://localhost:8080/api/analyze?path=/path/to/JavaClass.java"
```

## Configuration

### Environment Variables

- `SPRING_PORT`: Port for Spring Boot application (default: 8080)
- `PYTHON_CMD`: Python command to use (auto-detected)

### Script Configuration

Edit the configuration section in the workflow scripts:

```bash
# Configuration
SPRING_PORT=8080
LOG_DIR="${SCRIPT_DIR}/logs"
OUTPUT_DIR="${SCRIPT_DIR}/output"
```

## Generated Files

The workflow generates several types of files:

### XML Files
- **Location**: `.idea/demo/` and `output/`
- **Purpose**: Configuration files for UI components
- **Format**: Spring/FreeMarker XML templates

### HTTP Test Files
- **Location**: `httpRequests/` and `output/httpRequests/`
- **Purpose**: REST API test files for IDEs
- **Format**: HTTP request files

### JSON Files
- **Location**: `output/`
- **Purpose**: Analysis results and configuration data
- **Format**: Pretty-printed JSON

## Workflow Details

### 1. Prerequisites Check
- Verifies Java installation
- Verifies Python installation
- Checks for Spring Boot JAR (builds if missing)
- Validates Python scripts directory

### 2. Spring Boot Startup
- Kills any existing processes on port 8080
- Starts Spring Boot application in background
- Waits for application to be ready (max 60 seconds)
- Monitors application health

### 3. Python Script Execution
- Runs `main.py` orchestrator if available
- Falls back to individual script execution
- Handles missing scripts gracefully
- Logs all output for debugging

### 4. HTTP Test Generation
- Scans Java controllers for endpoints
- Generates individual test files
- Creates comprehensive test suite
- Supports various HTTP methods

### 5. Output Collection
- Copies XML files from generation directories
- Copies HTTP test files
- Copies JSON analysis results
- Organizes files in output directory

### 6. Git Operations (Optional)
- Pulls latest changes from remote
- Adds generated files to git
- Commits with timestamp
- Pushes changes to remote

### 7. Cleanup
- Stops Spring Boot application
- Removes PID files
- Preserves log files for debugging

## Troubleshooting

### Common Issues

1. **Port 8080 already in use**:
   ```bash
   # Find and kill the process
   lsof -ti:8080 | xargs kill -9
   ```

2. **Java not found**:
   ```bash
   # Install Java 17
   sudo apt install openjdk-17-jdk  # Ubuntu/Debian
   brew install openjdk@17          # macOS
   ```

3. **Python not found**:
   ```bash
   # Install Python 3
   sudo apt install python3 python3-pip  # Ubuntu/Debian
   brew install python@3.11              # macOS
   ```

4. **Maven build fails**:
   ```bash
   # Clean and rebuild
   cd spring-ftl
   ./mvnw clean
   ./mvnw package -DskipTests
   ```

### Log Files

Check the following log files for debugging:

- `logs/spring.log`: Spring Boot application logs
- `logs/python.log`: Python script execution logs
- Console output: Real-time workflow progress

### Debug Mode

Enable debug mode by modifying the scripts:

```bash
# Add to the beginning of the script
set -x  # Enable bash debugging
```

## CI/CD Integration

### GitHub Actions

The project includes a GitHub Actions workflow (`.github/workflows/main.yml`) that:

1. Builds the Spring Boot application
2. Creates Python executable with PyInstaller
3. Tests the workflow scripts
4. Creates distribution packages
5. Uploads artifacts

### Running Locally

To test the CI/CD workflow locally:

```bash
# Install act (GitHub Actions runner)
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run the workflow
act
```

## Development

### Adding New Python Scripts

1. Create the script in `spring-ftl/src/main/resources/scripts/`
2. Add it to the `scripts` list in `main.py`
3. Update the workflow scripts if needed

### Modifying the Workflow

1. Edit `run-xml-generator.sh` for Linux/macOS
2. Edit `run-xml-generator.bat` for Windows
3. Test both versions thoroughly
4. Update documentation

### Adding New REST Endpoints

1. Add endpoints to the Spring Boot controllers
2. Update `generate_http_tests.py` if needed
3. Test with the workflow

## License

This project is provided as-is for educational and development purposes.

## Support

For issues and questions:

1. Check the log files in `logs/`
2. Review this documentation
3. Check the GitHub Issues page
4. Run with `--help` flag for usage information