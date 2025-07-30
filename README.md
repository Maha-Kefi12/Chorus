# Spring Boot + Python XML Generator

This project combines a Spring Boot web application with Python scripts that generate XML files. The project can be built into standalone executables for easy distribution and deployment.

## Project Structure

- **Spring Boot Application** (`spring-ftl/`): Web application with REST APIs
- **Python Scripts** (`spring-ftl/src/main/resources/scripts/`): XML generation utilities
- **GitHub Workflows** (`.github/workflows/`): Automated build and release processes

## Features

- Spring Boot web application with REST endpoints
- Python-based XML generation from templates
- Automated executable building for multiple platforms
- HTTP API testing integration
- Cross-platform distribution packages

## Building Executables

### Automated Build (Recommended)

The project includes GitHub Actions workflows for automated building:

1. **Development Build**: Push to `main` branch triggers `build-executables.yml`
2. **Release Build**: Create a tag (e.g., `v1.0.0`) triggers `release.yml` for multi-platform builds

### Manual Build

#### Prerequisites
- Java 17+
- Python 3.11+
- Maven (included via wrapper)

#### Steps

1. **Build Spring Boot JAR**:
   ```bash
   cd spring-ftl
   ./mvnw clean package -DskipTests
   ```

2. **Build Python Executable**:
   ```bash
   pip install jinja2 pyinstaller
   pyinstaller main.spec --clean
   ```

3. **Create Distribution Package**:
   ```bash
   mkdir release-package
   cp spring-ftl/target/spring-ftl-*.jar release-package/spring-ftl.jar
   cp dist/main release-package/xml-generator
   ```

## Usage

### Quick Start
1. Download the appropriate package for your platform from the [Releases](../../releases) page
2. Extract the archive
3. Run the startup script:
   - Linux/macOS: `./start.sh`
   - Windows: `start.bat`

### Manual Execution
1. **Start Spring Boot Application**:
   ```bash
   java -jar spring-ftl.jar
   ```

2. **Run XML Generator** (in another terminal):
   ```bash
   ./xml-generator  # Linux/macOS
   xml-generator.exe  # Windows
   ```

### HTTP API Testing
The application includes automated HTTP tests that run against the REST endpoints:
```bash
curl http://localhost:8080/api/functionA
```

## Available Workflows

### 1. Build and Generate Executables (`.github/workflows/build-executables.yml`)
- Triggers on push to `main` or pull requests
- Builds both Java JAR and Python executable
- Runs HTTP tests
- Uploads build artifacts

### 2. Create Release (`.github/workflows/release.yml`)
- Triggers on version tags (`v*`)
- Builds for Linux, Windows, and macOS
- Creates GitHub release with downloadable packages
- Includes platform-specific startup scripts

### 3. HTTP API Tests (`.github/workflows/HTTP.yml`)
- Runs HTTP endpoint tests
- Validates API functionality

## Development

### Local Development Setup
1. Clone the repository
2. Install Java 17+ and Python 3.11+
3. Run the Spring Boot application: `cd spring-ftl && ./mvnw spring-boot:run`
4. Test the Python scripts: `python spring-ftl/src/main/resources/scripts/main.py`

### Adding New Features
1. Modify the Spring Boot application in `spring-ftl/src/main/java/`
2. Update Python scripts in `spring-ftl/src/main/resources/scripts/`
3. Update `main.spec` if new files need to be included in the executable
4. Test locally before pushing

## Release Process

1. **Create a new tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **GitHub Actions will automatically**:
   - Build executables for all platforms
   - Create a GitHub release
   - Upload distribution packages

3. **Users can download** platform-specific packages from the Releases page

## Requirements

- **Runtime**: Java 17+
- **Development**: Java 17+, Python 3.11+, Maven
- **Supported Platforms**: Linux x64, Windows x64, macOS x64

## Troubleshooting

- **Java not found**: Ensure Java 17+ is installed and in PATH
- **Python executable fails**: Check that all required Python dependencies are included in `main.spec`
- **Build failures**: Check GitHub Actions logs for detailed error messages
