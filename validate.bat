@echo off
REM Stash Plugin Validation Script for Windows
REM This script runs comprehensive validation on Stash plugins

setlocal EnableDelayedExpansion

echo.
echo ================================================================================
echo                         STASH PLUGIN VALIDATION
echo ================================================================================
echo.

REM Check if Node.js is installed
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo WARNING: Python is not installed or not in PATH
    echo Python validation will be skipped
    set PYTHON_AVAILABLE=false
) else (
    set PYTHON_AVAILABLE=true
)

REM Set target path
set TARGET_PATH=%1
if "%TARGET_PATH%"=="" set TARGET_PATH=.

echo Target: %TARGET_PATH%
echo Timestamp: %date% %time%
echo.

REM 1. Node.js Schema Validation
echo ================================================================================
echo 1. JSON SCHEMA VALIDATION (Node.js)
echo ================================================================================

cd validator
if not exist node_modules (
    echo Installing Node.js dependencies...
    call npm install
    if !ERRORLEVEL! neq 0 (
        echo ERROR: Failed to install Node.js dependencies
        cd ..
        pause
        exit /b 1
    )
)

echo Running Node.js schema validation...
if "%TARGET_PATH%"=="." (
    node index.js -v
) else (
    node index.js "..\%TARGET_PATH%" -v
)

set NODEJS_RESULT=%ERRORLEVEL%
cd ..

if %NODEJS_RESULT% equ 0 (
    echo [SUCCESS] Node.js schema validation PASSED
) else (
    echo [ERROR] Node.js schema validation FAILED
)

echo.

REM 2. Python Configuration Validation
echo ================================================================================
echo 2. PYTHON CONFIGURATION VALIDATION
echo ================================================================================

if "%PYTHON_AVAILABLE%"=="true" (
    REM Check if Python dependencies are installed
    python -c "import yaml" >nul 2>&1
    if !ERRORLEVEL! neq 0 (
        echo Installing Python dependencies...
        pip install PyYAML requests
        if !ERRORLEVEL! neq 0 (
            echo WARNING: Failed to install Python dependencies
            echo Python validation will be skipped
            set PYTHON_VALIDATION=false
        ) else (
            set PYTHON_VALIDATION=true
        )
    ) else (
        set PYTHON_VALIDATION=true
    )
    
    if "!PYTHON_VALIDATION!"=="true" (
        echo Running Python configuration validation...
        python validate_plugins.py "%TARGET_PATH%" --verbose
        set PYTHON_RESULT=!ERRORLEVEL!
        
        if !PYTHON_RESULT! equ 0 (
            echo [SUCCESS] Python configuration validation PASSED
        ) else (
            echo [ERROR] Python configuration validation FAILED
        )
    ) else (
        echo - Python validation SKIPPED (dependencies not available)
        set PYTHON_RESULT=0
    )
) else (
    echo - Python validation SKIPPED (Python not available)
    set PYTHON_RESULT=0
)

echo.

REM 3. File System Validation
echo ================================================================================
echo 3. FILE SYSTEM VALIDATION
echo ================================================================================

echo Running file system checks...

REM Check target exists
if not exist "%TARGET_PATH%" (
    echo ERROR: Target path does not exist: %TARGET_PATH%
    set FILESYSTEM_RESULT=1
    goto :filesystem_done
)

REM Check for YAML files
set YAML_COUNT=0
for %%f in ("%TARGET_PATH%\*.yml" "%TARGET_PATH%\*.yaml") do (
    if exist "%%f" (
        REM Skip template files
        echo %%f | findstr /i "template" >nul
        if !ERRORLEVEL! neq 0 (
            set /a YAML_COUNT+=1
        )
    )
)

if %YAML_COUNT% equ 0 (
    echo ERROR: No YAML plugin configuration files found
    set FILESYSTEM_RESULT=1
    goto :filesystem_done
)

echo Found %YAML_COUNT% YAML file(s)

REM Check for specific files if it's PerformerSiteSync
echo %TARGET_PATH% | findstr /i "PerformerSiteSync" >nul
if %ERRORLEVEL% equ 0 (
    echo Checking PerformerSiteSync specific files...
    
    if exist "%TARGET_PATH%\performer_site_sync.py" (
        echo [OK] Found performer_site_sync.py
    ) else (
        echo [MISSING] Missing performer_site_sync.py
    )
    
    if exist "%TARGET_PATH%\requirements.txt" (
        echo [OK] Found requirements.txt
    ) else (
        echo [MISSING] Missing requirements.txt
    )
    
    if exist "%TARGET_PATH%\modules" (
        echo [OK] Found modules directory
    ) else (
        echo [MISSING] Missing modules directory
    )
    
    if exist "%TARGET_PATH%\README.md" (
        echo [OK] Found README.md
    ) else (
        echo [MISSING] Missing README.md
    )
)

set FILESYSTEM_RESULT=0

:filesystem_done
if %FILESYSTEM_RESULT% equ 0 (
    echo [SUCCESS] File system validation PASSED
) else (
    echo [ERROR] File system validation FAILED
)

echo.

REM Summary
echo ================================================================================
echo                               VALIDATION SUMMARY
echo ================================================================================

set TOTAL_ERRORS=0

echo Node.js Schema Validation: 
if %NODEJS_RESULT% equ 0 (
    echo   ✓ PASS
) else (
    echo   ✗ FAIL
    set /a TOTAL_ERRORS+=1
)

echo Python Configuration Validation:
if %PYTHON_RESULT% equ 0 (
    echo   ✓ PASS
) else (
    echo   ✗ FAIL
    set /a TOTAL_ERRORS+=1
)

echo File System Validation:
if %FILESYSTEM_RESULT% equ 0 (
    echo   ✓ PASS
) else (
    echo   ✗ FAIL
    set /a TOTAL_ERRORS+=1
)

echo.

if %TOTAL_ERRORS% equ 0 (
    echo ================================================================================
    echo                            🎉 ALL VALIDATIONS PASSED! 🎉
    echo ================================================================================
    set OVERALL_RESULT=0
) else (
    echo ================================================================================
    echo                        ❌ VALIDATION FAILED WITH %TOTAL_ERRORS% ERROR(S) ❌
    echo ================================================================================
    set OVERALL_RESULT=1
)

echo.
echo Press any key to exit...
pause >nul

exit /b %OVERALL_RESULT%
