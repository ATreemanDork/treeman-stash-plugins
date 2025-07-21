# Development Guide

This document provides comprehensive guidelines for developing and maintaining Stash plugins in this repository.

## 📋 Table of Contents

- [Development Setup](#development-setup)
- [Plugin Structure](#plugin-structure)
- [Validation Process](#validation-process)
- [Testing Guidelines](#testing-guidelines)
- [Code Standards](#code-standards)
- [Documentation Requirements](#documentation-requirements)
- [Contribution Workflow](#contribution-workflow)
- [Release Process](#release-process)

## 🔧 Development Setup

### Prerequisites

1. **Stash**: Version 0.20.0 or later
2. **Python**: 3.8+ (for Python-based plugins)
3. **Node.js**: 18+ (for validation tools)
4. **PowerShell**: 7+ (for comprehensive validation scripts)
5. **Git**: For version control

### Environment Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ATreemanDork/treeman-stash-plugins.git
   cd treeman-stash-plugins
   ```

2. **Set Up Validation Tools**
   ```bash
   # Install Node.js dependencies
   cd validator
   npm install
   
   # Install Python dependencies (if using Python validation)
   pip install PyYAML requests
   ```

3. **Configure VS Code** (Optional)
   ```bash
   # Install recommended extensions
   code --install-extension ms-python.python
   code --install-extension redhat.vscode-yaml
   code --install-extension ms-vscode.powershell
   ```

### Development Environment Variables

Create a `.env` file in your development environment:

```bash
# Stash Configuration
STASH_URL=http://localhost:9999
STASH_API_KEY=your_api_key_here

# External APIs (for testing)
STASHDB_ENDPOINT=https://stashdb.org/graphql
STASHDB_API_KEY=your_stashdb_key

# Development Settings
DEBUG_MODE=true
CACHE_ENABLED=false
```

## 🏗️ Plugin Structure

### Standard Plugin Directory Structure

```
PluginName/
├── plugin_name.yml          # Plugin manifest (required)
├── plugin_name.py           # Main plugin script (for Python plugins)
├── plugin_name.js           # UI enhancements (optional)
├── README.md                # Plugin documentation (required)
├── requirements.txt         # Python dependencies (for Python plugins)
├── modules/                 # Modular code organization (recommended)
│   ├── __init__.py
│   ├── config.py
│   ├── api_client.py
│   └── utils.py
├── tests/                   # Unit tests (recommended)
│   ├── __init__.py
│   ├── test_config.py
│   └── test_api_client.py
└── docs/                    # Additional documentation (optional)
    ├── configuration.md
    └── troubleshooting.md
```

### Plugin Manifest (YAML) Requirements

Every plugin must include a properly formatted YAML manifest:

```yaml
# Required fields
name: PluginName                    # Plugin identifier
description: Brief plugin description
version: 1.0.0                     # Semantic versioning

# Execution configuration
exec:                              # Command to run plugin
  - python
  - "{pluginDir}/plugin_name.py"
interface: raw                     # raw, rpc, or js

# Optional but recommended
url: https://github.com/user/repo  # Plugin repository
ui:                               # UI enhancements
  javascript:
    - plugin_name.js
settings:                         # Plugin settings
  settingName:
    displayName: Setting Display Name
    description: Setting description
    type: STRING                  # STRING, NUMBER, BOOLEAN
    default: defaultValue
tasks:                           # Plugin tasks
  - name: Task Name
    description: Task description
    defaultArgs:
      mode: task_mode
hooks:                           # Event hooks (optional)
  - triggeredBy:
      - Performer.Update.Post
```

## ✅ Validation Process

### Automated Validation

We provide multiple validation tools to ensure plugin quality:

#### 1. Node.js Schema Validation

```bash
cd validator
npm run main                    # Validate all plugins
npm run main -- -v            # Verbose output
npm run main -- plugin.yml    # Validate specific file
```

#### 2. Python Configuration Validation

```bash
python validate_plugins.py              # Basic validation
python validate_plugins.py --verbose    # Detailed output
python validate_plugins.py --ci         # CI mode with exit codes
```

#### 3. Comprehensive PowerShell Validation

```powershell
.\validate_all.ps1                      # Validate everything
.\validate_all.ps1 -Verbose            # Detailed output
.\validate_all.ps1 -Path PluginName    # Validate specific plugin
.\validate_all.ps1 -CI                 # CI mode
```

### VS Code Integration

Use the built-in tasks for quick validation:

1. **Ctrl+Shift+P** → "Tasks: Run Task"
2. Select "Validate All Plugins" or "Validate PerformerSiteSync"

### Pre-commit Validation

Set up pre-commit hooks to automatically validate before commits:

```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "Running plugin validation..."
pwsh -File ./validate_all.ps1 -CI
if [ $? -ne 0 ]; then
    echo "❌ Validation failed. Commit aborted."
    exit 1
fi
echo "✅ Validation passed."
```

## 🧪 Testing Guidelines

### Unit Testing Structure

```python
# tests/test_plugin_module.py
import unittest
from unittest.mock import Mock, patch
from modules.plugin_module import PluginModule

class TestPluginModule(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = Mock()
        self.plugin = PluginModule(self.config)
    
    def test_initialization(self):
        """Test plugin initialization."""
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.config, self.config)
    
    @patch('modules.plugin_module.requests.post')
    def test_api_call(self, mock_post):
        """Test API call functionality."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': 'success'}
        mock_post.return_value = mock_response
        
        result = self.plugin.make_api_call()
        
        self.assertEqual(result['result'], 'success')
        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
# tests/test_integration.py
import unittest
from unittest.mock import Mock
import json
import sys
from pathlib import Path

# Add plugin to path
plugin_dir = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_dir))

from plugin_name import PluginMain

class TestPluginIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up integration test environment."""
        self.plugin = PluginMain()
    
    def test_full_workflow(self):
        """Test complete plugin workflow."""
        # Test configuration loading
        config_result = self.plugin.load_config()
        self.assertTrue(config_result['success'])
        
        # Test validation
        validation_result = self.plugin.validate_config()
        self.assertTrue(validation_result['valid'])
        
        # Test main functionality
        result = self.plugin.run_main_task()
        self.assertIsNotNone(result)
```

### Test Execution

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_plugin_module.py -v

# Run with coverage
python -m pytest tests/ --cov=modules --cov-report=html
```

## 📝 Code Standards

### Python Code Standards

Follow PEP 8 with these specific guidelines:

```python
# File header template
"""
Module description.

This module provides functionality for...
"""

import standard_library_modules
import third_party_modules
from local_modules import local_imports

# Class definitions
class ClassName:
    """Class description.
    
    Attributes:
        attribute_name (type): Description of attribute.
    """
    
    def __init__(self, param: str):
        """Initialize the class.
        
        Args:
            param (str): Description of parameter.
        """
        self.attribute_name = param
    
    def method_name(self, param: int) -> bool:
        """Method description.
        
        Args:
            param (int): Description of parameter.
            
        Returns:
            bool: Description of return value.
            
        Raises:
            ValueError: When parameter is invalid.
        """
        if param < 0:
            raise ValueError("Parameter must be non-negative")
        
        return param > 0

# Function definitions
def function_name(param: str) -> dict:
    """Function description.
    
    Args:
        param (str): Description of parameter.
        
    Returns:
        dict: Description of return value.
    """
    return {"result": param}
```

### JavaScript Code Standards

```javascript
/**
 * JavaScript code for Stash plugin UI enhancements.
 * 
 * This script provides additional UI functionality for the plugin.
 */

(function() {
    'use strict';
    
    // Constants
    const PLUGIN_NAME = 'PluginName';
    const VERSION = '1.0.0';
    
    /**
     * Initialize plugin UI enhancements.
     */
    function initializePlugin() {
        console.log(`Initializing ${PLUGIN_NAME} v${VERSION}`);
        
        // Add UI enhancements here
        addPluginStyles();
        bindEventHandlers();
    }
    
    /**
     * Add custom CSS styles for the plugin.
     */
    function addPluginStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .plugin-${PLUGIN_NAME.toLowerCase()} {
                /* Plugin-specific styles */
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Bind event handlers for plugin functionality.
     */
    function bindEventHandlers() {
        // Event handler implementation
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializePlugin);
    } else {
        initializePlugin();
    }
})();
```

### YAML Standards

```yaml
# Plugin manifest standards
name: PluginName                    # Use PascalCase
description: >                      # Use block scalar for long descriptions
  Comprehensive description of the plugin functionality.
  Include key features and use cases.
version: 1.0.0                     # Always use semantic versioning

# Use consistent indentation (2 spaces)
settings:
  settingName:
    displayName: Human Readable Name
    description: Clear, concise description
    type: STRING
    default: "default_value"
  
  numericSetting:
    displayName: Numeric Setting
    description: Description with valid range information
    type: NUMBER
    default: 42

# Group related tasks together
tasks:
  # Main functionality tasks
  - name: Primary Task
    description: Main plugin functionality
    defaultArgs:
      mode: primary_mode
  
  # Utility tasks
  - name: Validation Task
    description: Validate plugin configuration
    defaultArgs:
      mode: validate_config
```

### Error Handling Standards

```python
# Proper error handling and logging
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def safe_api_call(endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Make API call with proper error handling.
    
    Args:
        endpoint (str): API endpoint URL.
        data (Dict[str, Any]): Request data.
        
    Returns:
        Optional[Dict[str, Any]]: API response or None if failed.
    """
    try:
        response = requests.post(endpoint, json=data)
        response.raise_for_status()
        
        result = response.json()
        logger.debug(f"API call successful: {endpoint}")
        return result
        
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection failed to {endpoint}")
        return None
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout calling {endpoint}")
        return None
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code} from {endpoint}")
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed to {endpoint}: {str(e)}")
        return None
        
    except ValueError as e:
        logger.error(f"Invalid JSON response from {endpoint}: {str(e)}")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error calling {endpoint}: {str(e)}")
        return None
```

## 📚 Documentation Requirements

### README Structure

Every plugin must include a comprehensive README.md:

```markdown
# Plugin Name

Brief description of what the plugin does.

## Features

- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

## Installation

### Prerequisites
- Requirement 1
- Requirement 2

### Setup Instructions
1. Step 1
2. Step 2
3. Step 3

## Configuration

### Plugin Settings
- **Setting Name**: Description and valid values
- **Another Setting**: Description and default value

### External API Setup
Instructions for configuring external services.

## Usage

### Basic Operations
Instructions for common tasks.

### Advanced Features
Instructions for advanced functionality.

## Troubleshooting

### Common Issues
- **Issue**: Solution
- **Another Issue**: Solution

### Debug Information
How to enable debug logging and interpret output.

## Technical Details

### Dependencies
List of required dependencies.

### File Structure
Overview of plugin file organization.

### API Documentation
If applicable, document any APIs the plugin provides.

## License

License information.

## Support

How to get help or report issues.
```

### Code Documentation

- **All public functions and classes must have docstrings**
- **Use type hints for all function parameters and return values**
- **Include examples in docstrings for complex functions**
- **Document configuration options and their effects**

## 🔄 Contribution Workflow

### 1. Issue Creation

Before starting development:

1. **Search existing issues** to avoid duplicates
2. **Create detailed issue** with:
   - Clear problem description
   - Expected vs actual behavior
   - Steps to reproduce
   - Environment information
   - Proposed solution (if applicable)

### 2. Branch Strategy

```bash
# Create feature branch
git checkout -b feature/plugin-enhancement

# Create bugfix branch
git checkout -b bugfix/fix-validation-issue

# Create documentation branch
git checkout -b docs/update-readme
```

### 3. Development Process

1. **Write tests first** (TDD approach recommended)
2. **Implement functionality**
3. **Run validation tools**
4. **Update documentation**
5. **Test manually** with actual Stash instance

### 4. Commit Standards

Use conventional commit format:

```bash
# Feature commits
git commit -m "feat(plugin): add new validation feature"

# Bug fix commits
git commit -m "fix(validation): resolve schema validation issue"

# Documentation commits
git commit -m "docs(readme): update installation instructions"

# Refactoring commits
git commit -m "refactor(config): improve error handling"

# Test commits
git commit -m "test(api): add unit tests for API client"
```

### 5. Pull Request Process

1. **Ensure all validation passes**
2. **Include comprehensive description**
3. **Reference related issues**
4. **Add screenshots** for UI changes
5. **Request appropriate reviewers**

### Pull Request Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Validation tools pass

## Screenshots
Include screenshots for UI changes.

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)

## Related Issues
Fixes #123
Relates to #456
```

## 🚀 Release Process

### Version Management

Use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Update version numbers**
   - Plugin YAML manifest
   - Documentation
   - Package files

2. **Run comprehensive validation**
   ```bash
   pwsh -File ./validate_all.ps1 -CI
   ```

3. **Update CHANGELOG.md**
   ```markdown
   ## [1.2.0] - 2024-01-15
   
   ### Added
   - New feature description
   
   ### Changed
   - Modified functionality description
   
   ### Fixed
   - Bug fix description
   
   ### Security
   - Security improvement description
   ```

4. **Create release tag**
   ```bash
   git tag -a v1.2.0 -m "Release version 1.2.0"
   git push origin v1.2.0
   ```

5. **Create GitHub release**
   - Upload plugin archives
   - Include release notes
   - Mark as pre-release if applicable

### Automated Release

GitHub Actions workflow for automated releases:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Create Release Archive
      run: |
        cd PerformerSiteSync
        zip -r ../PerformerSiteSync-${{ github.ref_name }}.zip .
    
    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        files: |
          PerformerSiteSync-${{ github.ref_name }}.zip
        generate_release_notes: true
```

## 🔍 Quality Assurance

### Continuous Integration

All code changes must pass:

1. **Schema validation**
2. **Unit tests**
3. **Integration tests**
4. **Code quality checks**
5. **Security scans**
6. **Documentation validation**

### Performance Monitoring

Monitor plugin performance:

- **API response times**
- **Memory usage**
- **Cache hit rates**
- **Error rates**

### Security Considerations

1. **Never commit API keys or secrets**
2. **Validate all user inputs**
3. **Use parameterized queries**
4. **Implement rate limiting**
5. **Follow secure coding practices**

---

## 📞 Getting Help

### Resources

- **Documentation**: Check existing docs first
- **Issues**: Search GitHub issues
- **Discord**: Join the Stash community Discord
- **Code Review**: Request reviews from maintainers

### Contact

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Discord**: For real-time community support

---

**Happy coding! 🎉**
