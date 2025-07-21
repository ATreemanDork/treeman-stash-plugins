# Plugin Template

This directory contains templates and examples for creating new Stash plugins.

## Quick Start

1. **Copy Template Structure**
   ```bash
   cp -r _template YourPluginName
   cd YourPluginName
   ```

2. **Customize Files**
   - Rename `template_plugin.yml` to `your_plugin_name.yml`
   - Update all placeholder values
   - Implement your plugin logic

3. **Validate**
   ```bash
   cd ..
   .\validate.bat YourPluginName
   ```

## Template Files

- `template_plugin.yml` - Basic plugin manifest structure
- `README_template.md` - Documentation template
- `requirements.txt` - Python dependencies example
- `package.json` - Node.js dependencies example
- `.gitignore` - Common files to ignore

## Plugin Types

### Python Plugin
For data processing, API integrations, or complex logic:
- Use `exec: ["python", "{pluginDir}/script.py"]`
- Include `requirements.txt` for dependencies
- Follow Python code standards

### JavaScript Plugin  
For UI enhancements or simple operations:
- Use `interface: js`
- Include `package.json` if using Node.js dependencies
- Follow JavaScript code standards

### Mixed Plugin
Combining both Python backend and JavaScript frontend:
- Use Python for data processing
- Use JavaScript for UI enhancements
- Coordinate through Stash's plugin system

## Validation Requirements

All plugins must pass:
- ✅ Schema validation (YAML structure)
- ✅ File dependency checks
- ✅ Documentation completeness
- ✅ Code syntax validation

Run `../../validate.bat YourPluginName` before submitting.
