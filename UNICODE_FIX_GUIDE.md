# Unicode Encoding Fix Guide for Windows

This guide addresses the Unicode encoding error you encountered:
```
UnicodeEncodeError: 'charmap' codec can't encode characters in position 0-1: character maps to <undefined>
```

## 🔍 **What Caused the Error**

The error occurred because:
1. **Unicode Characters**: The Python script contained Unicode emoji characters (⚠️, ✅)
2. **Windows Console Encoding**: Windows Command Prompt uses CP1252 (Windows-1252) encoding by default
3. **Codec Mismatch**: CP1252 cannot encode Unicode emoji characters, causing the crash

## ✅ **Solutions Provided**

### 1. **Fixed Python Scripts**

#### `main.py` (Updated)
- ✅ Added `# -*- coding: utf-8 -*-` header
- ✅ Replaced Unicode emojis with ASCII text
- ✅ Added `safe_print()` function for encoding fallback
- ✅ Added UTF-8 encoding to subprocess calls
- ✅ Added Windows console UTF-8 setup

#### `main_windows.py` (New)
- ✅ Windows-specific version with robust encoding handling
- ✅ Forces UTF-8 output streams
- ✅ Multiple encoding fallbacks for file reading
- ✅ Enhanced error handling

### 2. **Windows Batch Files**

#### `run-python-scripts.bat`
- ✅ Sets console to UTF-8 encoding (`chcp 65001`)
- ✅ Sets Python environment variables for UTF-8
- ✅ Runs the appropriate Python script

#### `start-complete.bat`
- ✅ Complete workflow: Spring Boot + Python scripts
- ✅ Proper encoding setup
- ✅ Error handling for missing dependencies

## 🚀 **How to Use**

### Option 1: Run Python Scripts Only
```cmd
run-python-scripts.bat
```

### Option 2: Complete Application (Spring Boot + Python)
```cmd
start-complete.bat
```

### Option 3: Manual Python Execution
```cmd
# Set up encoding
chcp 65001
set PYTHONIOENCODING=utf-8

# Run the Windows-compatible script
cd spring-ftl\src\main\resources\scripts
python main_windows.py
```

## 🔧 **Technical Details**

### Environment Variables Set
```cmd
PYTHONIOENCODING=utf-8              # Forces UTF-8 for Python I/O
PYTHONLEGACYWINDOWSSTDIO=utf-8      # UTF-8 for Windows stdio
```

### Console Code Page
```cmd
chcp 65001    # Sets console to UTF-8 (65001)
```

### Python Script Changes
```python
# Before (caused error)
print(f"⚠️ Warning: Script {script} not found, skipping...")
print("✅ XML generation workflow completed!")

# After (works on Windows)
safe_print("WARNING: Script {} not found, skipping...".format(script))
safe_print("SUCCESS: XML generation workflow completed!")
```

## 🛠️ **Troubleshooting**

### Issue: "chcp is not recognized"
**Solution**: You're not in a Windows Command Prompt. Use `cmd.exe` instead of PowerShell.

### Issue: Python still shows encoding errors
**Solutions**:
1. **Use the Windows-specific script**:
   ```cmd
   python main_windows.py
   ```

2. **Set environment variables manually**:
   ```cmd
   set PYTHONIOENCODING=utf-8
   python main.py
   ```

3. **Use Python with explicit encoding**:
   ```cmd
   python -X utf8 main.py
   ```

### Issue: "python is not recognized"
**Solution**: Install Python and add it to PATH:
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Restart Command Prompt

### Issue: Scripts run but output is garbled
**Solution**: 
1. Ensure console is set to UTF-8: `chcp 65001`
2. Use a terminal that supports UTF-8 (Windows Terminal, VS Code terminal)

## 📋 **File Structure**

After applying the fixes, you should have:
```
your-directory/
├── start-complete.bat           # Complete workflow
├── run-python-scripts.bat      # Python scripts only
├── spring-ftl.jar              # Spring Boot application
└── spring-ftl/
    └── src/main/resources/scripts/
        ├── main.py              # Fixed original script
        ├── main_windows.py      # Windows-specific script
        ├── combined.py
        ├── mapping.py
        ├── lov_impl_.py
        └── screenfinal.py
```

## ✅ **Expected Results**

After using the fixed scripts, you should see:
```
========================================
  Python XML Generator Scripts
========================================

Setting up Python environment for UTF-8...
Console encoding: UTF-8 (65001)
Python IO encoding: utf-8

Python 3.x.x
Python environment configured for UTF-8

=== Running combined.py ===
[Script output without Unicode errors]
=== Finished combined.py ===

WARNING: Script mapping.py not found, skipping...
WARNING: Script lov_impl_.py not found, skipping...
WARNING: Script screenfinal.py not found, skipping...
SUCCESS: XML generation workflow completed!
```

## 🎯 **Key Differences**

| Before | After |
|--------|--------|
| Unicode emojis (⚠️, ✅) | ASCII text (WARNING, SUCCESS) |
| No encoding setup | UTF-8 console and Python setup |
| Single encoding attempt | Multiple encoding fallbacks |
| Basic error handling | Robust Windows-specific handling |
| Default CP1252 encoding | Forced UTF-8 encoding |

The fixes ensure your Python scripts run successfully on Windows without Unicode encoding errors!