#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Create a new Stash plugin from template

.DESCRIPTION
    This script creates a new plugin directory structure based on the template,
    with placeholder values replaced with actual plugin information.

.PARAMETER Name
    The name of the new plugin (will be used for directory and file names)

.PARAMETER Description
    Brief description of what the plugin does

.PARAMETER Author
    Plugin author name

.PARAMETER Type
    Plugin type: 'python' or 'javascript' or 'mixed'

.EXAMPLE
    .\new-plugin.ps1 -Name "MyAwesomePlugin" -Description "Does awesome things" -Author "Your Name" -Type "python"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Name,
    
    [Parameter(Mandatory=$true)]
    [string]$Description,
    
    [Parameter(Mandatory=$false)]
    [string]$Author = "Anonymous",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("python", "javascript", "mixed")]
    [string]$Type = "python"
)

# Validate plugin name
if ($Name -notmatch '^[A-Za-z][A-Za-z0-9_]*$') {
    Write-Error "Plugin name must start with a letter and contain only letters, numbers, and underscores"
    exit 1
}

# Check if plugin already exists
if (Test-Path $Name) {
    Write-Error "Plugin directory '$Name' already exists"
    exit 1
}

Write-Host "Creating new Stash plugin: $Name" -ForegroundColor Green
Write-Host "Description: $Description" -ForegroundColor Cyan
Write-Host "Author: $Author" -ForegroundColor Cyan
Write-Host "Type: $Type" -ForegroundColor Cyan
Write-Host ""

# Copy template directory
Write-Host "Copying template files..." -ForegroundColor Yellow
Copy-Item -Path "_template" -Destination $Name -Recurse

# Generate snake_case and lowercase versions for file naming
$snake_case_name = ($Name -creplace '([A-Z])', '_$1').ToLower().TrimStart('_')
$lowercase_name = $Name.ToLower()

# Rename template files
Write-Host "Renaming template files..." -ForegroundColor Yellow

# Rename YAML file
$yaml_src = Join-Path $Name "template_plugin.yml"
$yaml_dst = Join-Path $Name "$snake_case_name.yml"
if (Test-Path $yaml_src) {
    Rename-Item $yaml_src $yaml_dst
    Write-Host "  Renamed: template_plugin.yml -> $snake_case_name.yml" -ForegroundColor Gray
}

# Rename README template
$readme_src = Join-Path $Name "README_template.md"
$readme_dst = Join-Path $Name "README.md"
if (Test-Path $readme_src) {
    Rename-Item $readme_src $readme_dst
    Write-Host "  Renamed: README_template.md -> README.md" -ForegroundColor Gray
}

# Update file contents
Write-Host "Updating file contents..." -ForegroundColor Yellow

# Function to replace placeholders in file
function Update-FileContent {
    param($FilePath, $Replacements)
    
    if (Test-Path $FilePath) {
        $content = Get-Content $FilePath -Raw -Encoding UTF8
        
        foreach ($replacement in $Replacements.GetEnumerator()) {
            $content = $content -replace [regex]::Escape($replacement.Key), $replacement.Value
        }
        
        Set-Content $FilePath -Value $content -Encoding UTF8 -NoNewline
        Write-Host "  Updated: $(Split-Path $FilePath -Leaf)" -ForegroundColor Gray
    }
}

# Define replacements
$replacements = @{
    'TemplatePlugin' = $Name
    'template_plugin' = $snake_case_name
    'template-plugin' = $lowercase_name
    'A template plugin for creating new Stash plugins' = $Description
    'Brief description of what your plugin does and its main purpose.' = $Description
    'Your Name' = $Author
    'Template for Node.js-based Stash plugins' = "Node.js plugin: $Description"
}

# Update YAML configuration
$yaml_file = Join-Path $Name "$snake_case_name.yml"
Update-FileContent $yaml_file $replacements

# Update README
$readme_file = Join-Path $Name "README.md"
Update-FileContent $readme_file $replacements

# Update package.json if it exists
$package_file = Join-Path $Name "package.json"
Update-FileContent $package_file $replacements

# Create appropriate main file based on type
Write-Host "Creating main plugin file..." -ForegroundColor Yellow

switch ($Type) {
    "python" {
        $main_file = Join-Path $Name "$snake_case_name.py"
        @"
#!/usr/bin/env python3
"""
$Name Plugin for Stash
$Description
"""

import sys
import json
import stashapi.log as log
from typing import Dict, Any

def main():
    """Main entry point for the plugin"""
    try:
        # Parse command line arguments or JSON input
        if len(sys.argv) > 1:
            mode = sys.argv[1]
            args = sys.argv[2:] if len(sys.argv) > 2 else []
        else:
            # Try to read from stdin for JSON input
            try:
                json_input = json.loads(sys.stdin.read())
                mode = json_input.get('args', {}).get('mode', 'main_task')
                args = json_input.get('args', {})
            except (json.JSONDecodeError, AttributeError):
                mode = 'main_task'
                args = {}

        log.info(f"Starting $Name Plugin - Mode: {mode}")

        # Route to appropriate function based on mode
        if mode == 'main_task':
            result = main_task(args)
            log.info("Main task completed successfully")
            
        elif mode == 'test_connection':
            result = test_connection(args)
            log.info("Connection test completed")
            
        elif mode == 'clear_cache':
            result = clear_cache(args)
            log.info("Cache cleared")
            
        else:
            log.error(f"Unknown mode: {mode}")
            sys.exit(1)

        log.info("$Name Plugin completed successfully")

    except Exception as e:
        log.error(f"$Name Plugin failed: {str(e)}")
        sys.exit(1)

def main_task(args: Dict = None) -> Dict[str, Any]:
    """Primary plugin functionality"""
    log.info("Executing main task...")
    
    # TODO: Implement your main plugin logic here
    
    return {"status": "success", "message": "Main task completed"}

def test_connection(args: Dict = None) -> Dict[str, Any]:
    """Test external service connectivity"""
    log.info("Testing connections...")
    
    # TODO: Implement connection testing logic
    
    return {"status": "success", "message": "Connection test passed"}

def clear_cache(args: Dict = None) -> Dict[str, Any]:
    """Clear cached data"""
    log.info("Clearing cache...")
    
    # TODO: Implement cache clearing logic
    
    return {"status": "success", "message": "Cache cleared"}

if __name__ == "__main__":
    main()
"@ | Set-Content $main_file -Encoding UTF8
        Write-Host "  Created: $snake_case_name.py" -ForegroundColor Gray
    }
    
    "javascript" {
        # Update YAML for JavaScript plugin
        $yaml_content = Get-Content $yaml_file -Raw
        $yaml_content = $yaml_content -replace 'exec:\s*\n\s*-\s*python\s*\n\s*-\s*".*"', 'interface: js'
        Set-Content $yaml_file -Value $yaml_content -Encoding UTF8
        
        $main_file = Join-Path $Name "$snake_case_name.js"
        @"
/**
 * $Name Plugin for Stash
 * $Description
 */

(function() {
    'use strict';
    
    // Plugin configuration
    const PLUGIN_ID = '$Name';
    
    // Main plugin initialization
    function init() {
        console.log('$Name Plugin loaded');
        
        // TODO: Implement your JavaScript plugin logic here
        
        // Example: Add custom UI elements
        // addCustomUI();
        
        // Example: Hook into Stash events
        // setupEventListeners();
    }
    
    function addCustomUI() {
        // TODO: Add custom UI elements to Stash interface
        console.log('Adding custom UI elements...');
    }
    
    function setupEventListeners() {
        // TODO: Set up event listeners for Stash interface interactions
        console.log('Setting up event listeners...');
    }
    
    // Initialize plugin when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
"@ | Set-Content $main_file -Encoding UTF8
        Write-Host "  Created: $snake_case_name.js" -ForegroundColor Gray
    }
    
    "mixed" {
        # Create both Python and JavaScript files
        $python_file = Join-Path $Name "$snake_case_name.py"
        $js_file = Join-Path $Name "$snake_case_name.js"
        
        # Python backend (similar to python type but simpler)
        @"
#!/usr/bin/env python3
"""
$Name Plugin Backend for Stash
$Description
"""

import sys
import json
import stashapi.log as log

def main():
    """Main entry point for the plugin backend"""
    try:
        json_input = json.loads(sys.stdin.read())
        mode = json_input.get('args', {}).get('mode', 'main_task')
        
        log.info(f"Starting $Name Plugin Backend - Mode: {mode}")
        
        if mode == 'main_task':
            result = main_task()
        else:
            result = {"error": f"Unknown mode: {mode}"}
        
        print(json.dumps(result))
        
    except Exception as e:
        log.error(f"$Name Plugin Backend failed: {str(e)}")
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

def main_task():
    """Primary backend functionality"""
    # TODO: Implement backend logic
    return {"status": "success", "data": "Backend processing completed"}

if __name__ == "__main__":
    main()
"@ | Set-Content $python_file -Encoding UTF8

        # JavaScript frontend
        @"
/**
 * $Name Plugin Frontend for Stash
 * $Description
 */

(function() {
    'use strict';
    
    const PLUGIN_ID = '$Name';
    
    function init() {
        console.log('$Name Plugin Frontend loaded');
        
        // TODO: Implement frontend UI and interactions
        addCustomUI();
    }
    
    function addCustomUI() {
        // TODO: Add custom UI elements
        console.log('Adding custom UI for $Name...');
    }
    
    // Call backend when needed
    function callBackend(mode, data = {}) {
        // TODO: Implement backend communication
        console.log(`Calling backend with mode: ${mode}`);
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
"@ | Set-Content $js_file -Encoding UTF8

        # Update YAML to include both files
        $yaml_content = Get-Content $yaml_file -Raw
        $ui_section = @"
ui:
  javascript:
    - $snake_case_name.js
"@
        $yaml_content = $yaml_content -replace '(interface: raw)', "$1`n$ui_section"
        Set-Content $yaml_file -Value $yaml_content -Encoding UTF8
        
        Write-Host "  Created: $snake_case_name.py (backend)" -ForegroundColor Gray
        Write-Host "  Created: $snake_case_name.js (frontend)" -ForegroundColor Gray
    }
}

# Clean up unnecessary files based on type
if ($Type -eq "javascript") {
    $requirements_file = Join-Path $Name "requirements.txt"
    if (Test-Path $requirements_file) {
        Remove-Item $requirements_file
        Write-Host "  Removed: requirements.txt (not needed for JavaScript plugin)" -ForegroundColor Gray
    }
} elseif ($Type -eq "python") {
    $package_file = Join-Path $Name "package.json"
    if (Test-Path $package_file) {
        Remove-Item $package_file
        Write-Host "  Removed: package.json (not needed for Python plugin)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "✅ Plugin '$Name' created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. cd $Name" -ForegroundColor White
Write-Host "2. Edit the main plugin file(s) to implement your logic" -ForegroundColor White
Write-Host "3. Update README.md with specific usage instructions" -ForegroundColor White
Write-Host "4. Test your plugin: cd .. && .\validate.bat $Name" -ForegroundColor White
Write-Host "5. Install in Stash and test functionality" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Cyan
