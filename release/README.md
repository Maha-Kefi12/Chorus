# Spring FTL Application Package

## Quick Start

### For Complete Workflow (Recommended):
1. Extract all files to a directory
2. Double-click `start.bat` to open the launcher menu
3. Choose option 4 for "Workflow complet (Spring Boot + XML)"
4. Follow the on-screen instructions

### For Individual Components:
- **Spring Boot only**: Use `start-server.bat`
- **XML Generator only**: Use `start-xml.bat`  
- **Sequential workflow**: Use `start-server-then-xml.bat`

## What's Included

### Main Applications
- `spring-ftl.jar` - Spring Boot web application with REST API
- `xml-generator.exe` - XML file generator (if included)

### Batch Scripts
- `start.bat` - Interactive menu launcher with 9 different options
- `start-server.bat` - Spring Boot server only
- `start-xml.bat` - XML generator only
- `start-server-then-xml.bat` - Run server, then XML generator
- `start-debug.bat` - Debug mode with detailed output

### HTTP Test Files
- `httpRequests/` - Directory containing HTTP endpoint test files
- `comprehensive-api-tests.http` - Complete API test collection

## Features

### Spring Boot Application
The Spring Boot server provides a REST API with endpoints for:
- Code analysis and parsing
- Function extraction
- Data transformation
- Field mapping and ordering

**Available Endpoints:**
- `GET /api/analyze` - Analyze code structure
- `GET /api/extract-function?path=<file>` - Extract functions from file
- `GET /api/extract-function-name?path=<file>` - Extract function names
- `POST /api/parser/fromCode` - Parse code from request body
- `POST /transform/updateFieldOrder` - Update field ordering
- `POST /transform/save-transformation` - Save transformations

### XML Generator
Generates XML configuration files in the `.idea/demo` directory by:
1. Combining data from multiple sources
2. Creating field mappings
3. Generating LOV implementations
4. Creating final screen configurations

**Multi-Form Support:**
The XML generator now supports multiple form types, not just "aini". It can:
- Automatically detect available forms from your data
- Generate XML files for each detected form
- Use dynamic form IDs and bean names
- Create separate output directories for each form

**Supported Form Types:**
- `aini` - Default form (backward compatibility)
- `user` - User management forms
- `product` - Product management forms
- Any custom form type defined in your data

## Launcher Menu Options

When you run `start.bat`, you'll see these options:

1. **Diagnostic complet** - Full environment diagnostic
2. **Correction automatique** - Automatic problem fixing
3. **Démarrage en mode administrateur** - Administrator mode startup
4. **Workflow complet** - Complete workflow (Spring Boot + XML)
5. **Workflow temps réel** - Real-time workflow with monitoring
6. **XML Generator seulement** - XML Generator only
7. **Spring Boot seulement** - Spring Boot only
8. **Spring Boot puis XML Generator** - Sequential execution
9. **XML Generator puis Spring Boot** - Reverse sequential execution
10. **Diagnostic compatibilité 64-bit** - 64-bit compatibility diagnostic
0. **Quitter** - Exit

## Requirements

- **Java 17 or later** (for Spring Boot application)
- **Windows OS** (for batch scripts and XML generator)
- **Internet connection** (for downloading dependencies on first run)
- **Write permissions** in the application directory

## Troubleshooting

### If the Spring Boot application won't start:
1. Check that Java 17+ is installed: `java -version`
2. Ensure port 8080 is available
3. Try the diagnostic option (1) in the launcher menu
4. Try the automatic fix option (2) in the launcher menu
5. Run as administrator if needed (option 3)

### If no XML files are generated:
1. Use `start-debug.bat` for detailed error information
2. Check write permissions in the directory
3. Ensure all required files are present
4. Verify the `.idea/demo` directory can be created

### If XML generator has 64-bit compatibility issues:
1. Run `64bit-diagnostic.bat` to check system compatibility
2. Install Visual C++ Redistributable 2015-2022 (x64)
3. Try running as administrator
4. Check Windows Defender/Antivirus exclusions
5. Try running in Windows compatibility mode
6. Ensure you have the latest Windows updates

### If HTTP endpoints don't respond:
1. Wait 30-60 seconds for the server to fully start
2. Check that the server is running on http://localhost:8080
3. Try accessing http://localhost:8080/api/analyze in a browser
4. Check firewall settings

### If XML generator only works with "aini":
The XML generator now supports multiple form types. If you're only seeing "aini" forms:

1. **Check your data structure**: Ensure your `transformed_result.json` contains multiple forms
2. **Verify form detection**: The generator automatically detects forms from your data
3. **Use environment variables**: Set `FORM_ID=your_form_name` to target a specific form
4. **Check output directories**: Each form gets its own directory in `.idea/demo/`

## Usage Examples

### Testing API Endpoints
Use the provided HTTP test files in your IDE or with curl:

```bash
# Test the analyze endpoint
curl http://localhost:8080/api/analyze

# Test code parsing
curl -X POST -H "Content-Type: text/plain" \
     -d "public class Test { }" \
     http://localhost:8080/api/parser/fromCode
```

### Complete Workflow
1. Start the launcher: `start.bat`
2. Choose option 4 (Complete workflow)
3. The system will:
   - Start Spring Boot server
   - Test all API endpoints
   - Generate XML files for all detected forms
   - Collect final data
   - Provide summary report

### Multi-Form XML Generation
The XML generator now supports multiple forms:

```bash
# Generate XML for all detected forms
xml-generator.exe

# Generate XML for a specific form
set FORM_ID=user
xml-generator.exe

# Generate XML for another form
set FORM_ID=product
xml-generator.exe
```

## Output Files

### Server Data
When using workflow options, data is saved in the `output/` directory:
- `analyze_response.json` - Analysis results
- `parser_fromcode_response.json` - Code parsing results  
- `extract_function_*.json` - Function extraction results
- Various transformation results

### XML Files
Generated XML files are placed in `.idea/demo/` with form-specific subdirectories:
- `.idea/demo/aini/` - Aini form XML files
- `.idea/demo/user/` - User form XML files
- `.idea/demo/product/` - Product form XML files
- Other form directories as detected

Each form directory contains:
- `{form_id}.block.xml` - Main form configuration
- `{form_id}.block.properties` - Form properties
- Other XML files as needed

## Development Notes

This package combines a Spring Boot web application with XML generation tools,
designed for code analysis and configuration file generation workflows.

The batch scripts provide multiple execution modes to suit different use cases,
from simple individual component execution to complex integrated workflows
with real-time monitoring and data collection.

**Multi-Form Architecture:**
The XML generator has been enhanced to support multiple form types:
- **Dynamic Form Detection**: Automatically detects available forms from data
- **Flexible Bean Naming**: Uses form-specific bean IDs (e.g., `userFormService`)
- **Separate Output Directories**: Each form gets its own output directory
- **Backward Compatibility**: Still works with existing "aini" forms
- **Environment Variable Support**: Can target specific forms via `FORM_ID`

This makes the system much more flexible and suitable for projects with multiple form types. 