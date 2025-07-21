#!/bin/bash

# Stash Plugin Validation Script for Linux/macOS
# This script runs comprehensive validation on Stash plugins

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Symbols
CHECK_MARK="✓"
CROSS_MARK="✗"
WARNING="⚠"
INFO="ℹ"

echo ""
echo "================================================================================"
echo "                         STASH PLUGIN VALIDATION"
echo "================================================================================"
echo ""

# Check arguments
TARGET_PATH="${1:-.}"
VERBOSE="${2:-false}"

if [ "$2" = "-v" ] || [ "$2" = "--verbose" ]; then
    VERBOSE="true"
fi

echo "Target: $TARGET_PATH"
echo "Timestamp: $(date)"
echo ""

# Initialize result variables
NODEJS_RESULT=0
PYTHON_RESULT=0
FILESYSTEM_RESULT=0
TOTAL_ERRORS=0

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js is not installed or not in PATH${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
PYTHON_AVAILABLE=false
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_AVAILABLE=true
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_AVAILABLE=true
else
    echo -e "${YELLOW}WARNING: Python is not installed or not in PATH${NC}"
    echo "Python validation will be skipped"
fi

# 1. Node.js Schema Validation
echo "================================================================================"
echo "1. JSON SCHEMA VALIDATION (Node.js)"
echo "================================================================================"

cd validator
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to install Node.js dependencies${NC}"
        exit 1
    fi
fi

echo "Running Node.js schema validation..."
if [ "$TARGET_PATH" = "." ]; then
    if [ "$VERBOSE" = "true" ]; then
        node index.js -v
    else
        node index.js
    fi
else
    if [ "$VERBOSE" = "true" ]; then
        node index.js "../$TARGET_PATH" -v
    else
        node index.js "../$TARGET_PATH"
    fi
fi

NODEJS_RESULT=$?
cd ..

if [ $NODEJS_RESULT -eq 0 ]; then
    echo -e "${GREEN}$CHECK_MARK Node.js schema validation PASSED${NC}"
else
    echo -e "${RED}$CROSS_MARK Node.js schema validation FAILED${NC}"
    ((TOTAL_ERRORS++))
fi

echo ""

# 2. Python Configuration Validation
echo "================================================================================"
echo "2. PYTHON CONFIGURATION VALIDATION"
echo "================================================================================"

if [ "$PYTHON_AVAILABLE" = "true" ]; then
    # Check if Python dependencies are installed
    if ! $PYTHON_CMD -c "import yaml" &> /dev/null; then
        echo "Installing Python dependencies..."
        $PYTHON_CMD -m pip install PyYAML requests
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}WARNING: Failed to install Python dependencies${NC}"
            echo "Python validation will be skipped"
            PYTHON_VALIDATION=false
        else
            PYTHON_VALIDATION=true
        fi
    else
        PYTHON_VALIDATION=true
    fi
    
    if [ "$PYTHON_VALIDATION" = "true" ]; then
        echo "Running Python configuration validation..."
        if [ "$VERBOSE" = "true" ]; then
            $PYTHON_CMD validate_plugins.py "$TARGET_PATH" --verbose
        else
            $PYTHON_CMD validate_plugins.py "$TARGET_PATH"
        fi
        PYTHON_RESULT=$?
        
        if [ $PYTHON_RESULT -eq 0 ]; then
            echo -e "${GREEN}$CHECK_MARK Python configuration validation PASSED${NC}"
        else
            echo -e "${RED}$CROSS_MARK Python configuration validation FAILED${NC}"
            ((TOTAL_ERRORS++))
        fi
    else
        echo -e "${YELLOW}- Python validation SKIPPED (dependencies not available)${NC}"
    fi
else
    echo -e "${YELLOW}- Python validation SKIPPED (Python not available)${NC}"
fi

echo ""

# 3. File System Validation
echo "================================================================================"
echo "3. FILE SYSTEM VALIDATION"
echo "================================================================================"

echo "Running file system checks..."

# Check target exists
if [ ! -e "$TARGET_PATH" ]; then
    echo -e "${RED}ERROR: Target path does not exist: $TARGET_PATH${NC}"
    FILESYSTEM_RESULT=1
else
    # Check for YAML files (excluding templates)
    YAML_COUNT=$(find "$TARGET_PATH" -maxdepth 1 -name "*.yml" -o -name "*.yaml" | grep -v template | wc -l)
    
    if [ $YAML_COUNT -eq 0 ]; then
        echo -e "${RED}ERROR: No YAML plugin configuration files found${NC}"
        FILESYSTEM_RESULT=1
    else
        echo "Found $YAML_COUNT YAML file(s)"
        
        # Check for specific files if it's PerformerSiteSync
        if [[ "$TARGET_PATH" == *"PerformerSiteSync"* ]]; then
            echo "Checking PerformerSiteSync specific files..."
            
            if [ -f "$TARGET_PATH/performer_site_sync.py" ]; then
                echo -e "${GREEN}$CHECK_MARK Found performer_site_sync.py${NC}"
            else
                echo -e "${RED}$CROSS_MARK Missing performer_site_sync.py${NC}"
            fi
            
            if [ -f "$TARGET_PATH/requirements.txt" ]; then
                echo -e "${GREEN}$CHECK_MARK Found requirements.txt${NC}"
            else
                echo -e "${RED}$CROSS_MARK Missing requirements.txt${NC}"
            fi
            
            if [ -d "$TARGET_PATH/modules" ]; then
                echo -e "${GREEN}$CHECK_MARK Found modules directory${NC}"
            else
                echo -e "${RED}$CROSS_MARK Missing modules directory${NC}"
            fi
            
            if [ -f "$TARGET_PATH/README.md" ]; then
                echo -e "${GREEN}$CHECK_MARK Found README.md${NC}"
            else
                echo -e "${RED}$CROSS_MARK Missing README.md${NC}"
            fi
        fi
        
        FILESYSTEM_RESULT=0
    fi
fi

if [ $FILESYSTEM_RESULT -eq 0 ]; then
    echo -e "${GREEN}$CHECK_MARK File system validation PASSED${NC}"
else
    echo -e "${RED}$CROSS_MARK File system validation FAILED${NC}"
    ((TOTAL_ERRORS++))
fi

echo ""

# Summary
echo "================================================================================"
echo "                               VALIDATION SUMMARY"
echo "================================================================================"

echo "Node.js Schema Validation:"
if [ $NODEJS_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}$CHECK_MARK PASS${NC}"
else
    echo -e "  ${RED}$CROSS_MARK FAIL${NC}"
fi

echo "Python Configuration Validation:"
if [ $PYTHON_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}$CHECK_MARK PASS${NC}"
else
    echo -e "  ${RED}$CROSS_MARK FAIL${NC}"
fi

echo "File System Validation:"
if [ $FILESYSTEM_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}$CHECK_MARK PASS${NC}"
else
    echo -e "  ${RED}$CROSS_MARK FAIL${NC}"
fi

echo ""

if [ $TOTAL_ERRORS -eq 0 ]; then
    echo "================================================================================"
    echo -e "                        ${GREEN}🎉 ALL VALIDATIONS PASSED! 🎉${NC}"
    echo "================================================================================"
    exit 0
else
    echo "================================================================================"
    echo -e "                    ${RED}❌ VALIDATION FAILED WITH $TOTAL_ERRORS ERROR(S) ❌${NC}"
    echo "================================================================================"
    exit 1
fi
