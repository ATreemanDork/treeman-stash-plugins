#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Comprehensive validation script for Stash plugins using both Node.js and Python validators.

.DESCRIPTION
    This script runs multiple validation checks on Stash plugins:
    1. JSON Schema validation using the Node.js validator
    2. Python-based configuration validation
    3. File existence checks
    4. Plugin-specific validation (for PerformerSiteSync)

.PARAMETER Path
    Path to plugin file or directory to validate

.PARAMETER Verbose
    Enable verbose output

.PARAMETER ContinueOnError
    Continue validation even after encountering errors

.PARAMETER AllowDeprecated
    Allow deprecated features in plugin configurations

.PARAMETER CI
    CI mode: exit with error code if validation fails

.EXAMPLE
    .\validate_all.ps1 -Path PerformerSiteSync
    
.EXAMPLE
    .\validate_all.ps1 -Verbose -CI
#>

param(
    [string]$Path = ".",
    [switch]$Verbose,
    [switch]$ContinueOnError,
    [switch]$AllowDeprecated,
    [switch]$CI
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Color functions for output
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️ $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️ $Message" -ForegroundColor Cyan
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Blue
    Write-Host $Title -ForegroundColor Blue
    Write-Host "=" * 60 -ForegroundColor Blue
}

# Main validation function
function Invoke-PluginValidation {
    param(
        [string]$TargetPath,
        [bool]$IsVerbose,
        [bool]$ContinueOnErrors,
        [bool]$AllowDeprecatedFeatures,
        [bool]$CIMode
    )
    
    $validationResults = @{
        OverallSuccess = $true
        NodeJsValidation = $null
        PythonValidation = $null
        FileChecks = $null
        PluginSpecific = $null
        Errors = @()
        Warnings = @()
    }
    
    Write-Header "STASH PLUGIN COMPREHENSIVE VALIDATION"
    Write-Info "Target: $TargetPath"
    Write-Info "Timestamp: $(Get-Date)"
    
    # Check if target exists
    if (-not (Test-Path $TargetPath)) {
        Write-Error-Custom "Target path does not exist: $TargetPath"
        $validationResults.OverallSuccess = $false
        $validationResults.Errors += "Target path does not exist"
        return $validationResults
    }
    
    # Step 1: Node.js Schema Validation
    Write-Header "1. JSON SCHEMA VALIDATION (Node.js)"
    $validationResults.NodeJsValidation = Invoke-NodeJsValidation -Path $TargetPath -Verbose:$IsVerbose -ContinueOnError:$ContinueOnErrors -AllowDeprecated:$AllowDeprecatedFeatures
    
    if (-not $validationResults.NodeJsValidation.Success) {
        $validationResults.OverallSuccess = $false
        $validationResults.Errors += $validationResults.NodeJsValidation.Errors
    }
    
    # Step 2: Python Configuration Validation
    Write-Header "2. PYTHON CONFIGURATION VALIDATION"
    $validationResults.PythonValidation = Invoke-PythonValidation -Path $TargetPath -Verbose:$IsVerbose
    
    if (-not $validationResults.PythonValidation.Success) {
        $validationResults.OverallSuccess = $false
        $validationResults.Errors += $validationResults.PythonValidation.Errors
    }
    
    # Step 3: File System Validation
    Write-Header "3. FILE SYSTEM VALIDATION"
    $validationResults.FileChecks = Invoke-FileSystemValidation -Path $TargetPath -Verbose:$IsVerbose
    
    if (-not $validationResults.FileChecks.Success) {
        $validationResults.OverallSuccess = $false
        $validationResults.Errors += $validationResults.FileChecks.Errors
    }
    $validationResults.Warnings += $validationResults.FileChecks.Warnings
    
    # Step 4: Plugin-Specific Validation
    Write-Header "4. PLUGIN-SPECIFIC VALIDATION"
    $validationResults.PluginSpecific = Invoke-PluginSpecificValidation -Path $TargetPath -Verbose:$IsVerbose
    
    if (-not $validationResults.PluginSpecific.Success) {
        $validationResults.OverallSuccess = $false
        $validationResults.Errors += $validationResults.PluginSpecific.Errors
    }
    $validationResults.Warnings += $validationResults.PluginSpecific.Warnings
    
    # Summary
    Write-Header "VALIDATION SUMMARY"
    if ($validationResults.OverallSuccess) {
        Write-Success "All validations passed!"
    } else {
        Write-Error-Custom "Validation failed with $($validationResults.Errors.Count) errors"
    }
    
    if ($validationResults.Warnings.Count -gt 0) {
        Write-Warning-Custom "$($validationResults.Warnings.Count) warnings found"
    }
    
    if ($IsVerbose -or -not $validationResults.OverallSuccess) {
        Write-Info "Node.js Validation: $(if ($validationResults.NodeJsValidation.Success) { '✅ Pass' } else { '❌ Fail' })"
        Write-Info "Python Validation: $(if ($validationResults.PythonValidation.Success) { '✅ Pass' } else { '❌ Fail' })"
        Write-Info "File System Checks: $(if ($validationResults.FileChecks.Success) { '✅ Pass' } else { '❌ Fail' })"
        Write-Info "Plugin-Specific: $(if ($validationResults.PluginSpecific.Success) { '✅ Pass' } else { '❌ Fail' })"
    }
    
    return $validationResults
}

function Invoke-NodeJsValidation {
    param(
        [string]$Path,
        [bool]$Verbose,
        [bool]$ContinueOnError,
        [bool]$AllowDeprecated
    )
    
    $result = @{
        Success = $true
        Errors = @()
        Warnings = @()
        Output = ""
    }
    
    try {
        # Check if Node.js validator exists
        $validatorPath = Join-Path $PSScriptRoot "validator"
        if (-not (Test-Path $validatorPath)) {
            $result.Errors += "Node.js validator directory not found"
            $result.Success = $false
            return $result
        }
        
        # Check if node_modules exists
        $nodeModulesPath = Join-Path $validatorPath "node_modules"
        if (-not (Test-Path $nodeModulesPath)) {
            Write-Warning-Custom "Node.js dependencies not installed. Running npm install..."
            Push-Location $validatorPath
            try {
                npm install
                if ($LASTEXITCODE -ne 0) {
                    $result.Errors += "Failed to install Node.js dependencies"
                    $result.Success = $false
                    return $result
                }
            } finally {
                Pop-Location
            }
        }
        
        # Build validator arguments
        $args = @()
        if ($Verbose) { $args += "-v" }
        if ($ContinueOnError) { $args += "-a" }
        if ($AllowDeprecated) { $args += "-d" }
        $args += $Path
        
        # Run Node.js validator
        Push-Location $validatorPath
        try {
            $output = node index.js @args 2>&1
            $exitCode = $LASTEXITCODE
            
            $result.Output = $output -join "`n"
            
            if ($exitCode -eq 0) {
                Write-Success "Node.js schema validation passed"
            } else {
                Write-Error-Custom "Node.js schema validation failed"
                $result.Success = $false
                $result.Errors += "Schema validation failed"
            }
            
            if ($Verbose) {
                Write-Host $result.Output
            }
            
        } finally {
            Pop-Location
        }
        
    } catch {
        $result.Errors += "Error running Node.js validator: $($_.Exception.Message)"
        $result.Success = $false
        Write-Error-Custom "Node.js validation error: $($_.Exception.Message)"
    }
    
    return $result
}

function Invoke-PythonValidation {
    param(
        [string]$Path,
        [bool]$Verbose
    )
    
    $result = @{
        Success = $true
        Errors = @()
        Warnings = @()
        Output = ""
    }
    
    try {
        # Check if Python is available
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCmd) {
            $result.Warnings += "Python not found in PATH - skipping Python validation"
            Write-Warning-Custom "Python not found - skipping Python validation"
            return $result
        }
        
        # Check if Python validation script exists
        $pythonValidatorPath = Join-Path $PSScriptRoot "validate_plugins.py"
        if (-not (Test-Path $pythonValidatorPath)) {
            $result.Warnings += "Python validator script not found - skipping Python validation"
            Write-Warning-Custom "Python validator not found - skipping Python validation"
            return $result
        }
        
        # Build Python validator arguments
        $args = @($pythonValidatorPath)
        if ($Verbose) { $args += "--verbose" }
        $args += $Path
        
        # Run Python validator
        $output = & python @args 2>&1
        $exitCode = $LASTEXITCODE
        
        $result.Output = $output -join "`n"
        
        if ($exitCode -eq 0) {
            Write-Success "Python configuration validation passed"
        } else {
            Write-Warning-Custom "Python configuration validation had issues"
            $result.Warnings += "Python validation found issues"
        }
        
        if ($Verbose) {
            Write-Host $result.Output
        }
        
    } catch {
        $result.Warnings += "Error running Python validator: $($_.Exception.Message)"
        Write-Warning-Custom "Python validation error: $($_.Exception.Message)"
    }
    
    return $result
}

function Invoke-FileSystemValidation {
    param(
        [string]$Path,
        [bool]$Verbose
    )
    
    $result = @{
        Success = $true
        Errors = @()
        Warnings = @()
        CheckedFiles = @()
    }
    
    try {
        $targetPath = Resolve-Path $Path
        
        if ((Get-Item $targetPath).PSIsContainer) {
            # Directory validation
            $yamlFiles = Get-ChildItem -Path $targetPath -Filter "*.yml" -ErrorAction SilentlyContinue
            $yamlFiles += Get-ChildItem -Path $targetPath -Filter "*.yaml" -ErrorAction SilentlyContinue
            
            if ($yamlFiles.Count -eq 0) {
                $result.Errors += "No YAML plugin configuration files found in directory"
                $result.Success = $false
                Write-Error-Custom "No plugin YAML files found"
                return $result
            }
            
            foreach ($yamlFile in $yamlFiles) {
                $fileResult = Test-PluginFileStructure -YamlFile $yamlFile.FullName -Verbose:$Verbose
                $result.CheckedFiles += $fileResult
                
                if (-not $fileResult.Success) {
                    $result.Success = $false
                    $result.Errors += $fileResult.Errors
                }
                $result.Warnings += $fileResult.Warnings
            }
        } else {
            # Single file validation
            $fileResult = Test-PluginFileStructure -YamlFile $targetPath -Verbose:$Verbose
            $result.CheckedFiles += $fileResult
            
            if (-not $fileResult.Success) {
                $result.Success = $false
                $result.Errors += $fileResult.Errors
            }
            $result.Warnings += $fileResult.Warnings
        }
        
        if ($result.Success) {
            Write-Success "File system validation passed"
        } else {
            Write-Error-Custom "File system validation failed"
        }
        
    } catch {
        $result.Errors += "File system validation error: $($_.Exception.Message)"
        $result.Success = $false
        Write-Error-Custom "File system validation error: $($_.Exception.Message)"
    }
    
    return $result
}

function Test-PluginFileStructure {
    param(
        [string]$YamlFile,
        [bool]$Verbose
    )
    
    $result = @{
        File = $YamlFile
        Success = $true
        Errors = @()
        Warnings = @()
    }
    
    try {
        $pluginDir = Split-Path $YamlFile -Parent
        $yamlContent = Get-Content $YamlFile -Raw | ConvertFrom-Yaml -ErrorAction SilentlyContinue
        
        if (-not $yamlContent) {
            $result.Errors += "Failed to parse YAML content"
            $result.Success = $false
            return $result
        }
        
        # Check UI files
        if ($yamlContent.ui) {
            if ($yamlContent.ui.css) {
                $cssFiles = if ($yamlContent.ui.css -is [array]) { $yamlContent.ui.css } else { @($yamlContent.ui.css) }
                foreach ($cssFile in $cssFiles) {
                    $fullPath = Join-Path $pluginDir $cssFile
                    if (-not (Test-Path $fullPath)) {
                        $result.Warnings += "CSS file not found: $cssFile"
                    } else {
                        if ($Verbose) { Write-Info "Found CSS file: $cssFile" }
                    }
                }
            }
            
            if ($yamlContent.ui.javascript) {
                $jsFiles = if ($yamlContent.ui.javascript -is [array]) { $yamlContent.ui.javascript } else { @($yamlContent.ui.javascript) }
                foreach ($jsFile in $jsFiles) {
                    $fullPath = Join-Path $pluginDir $jsFile
                    if (-not (Test-Path $fullPath)) {
                        $result.Warnings += "JavaScript file not found: $jsFile"
                    } else {
                        if ($Verbose) { Write-Info "Found JavaScript file: $jsFile" }
                    }
                }
            }
        }
        
        # Check exec files (for external plugins)
        if ($yamlContent.exec -and $yamlContent.interface -ne "js") {
            $execFile = $yamlContent.exec[0]
            if ($execFile -ne "python" -and $execFile -ne "node") {
                $fullPath = Join-Path $pluginDir $execFile
                if (-not (Test-Path $fullPath)) {
                    $result.Errors += "Executable file not found: $execFile"
                    $result.Success = $false
                } else {
                    if ($Verbose) { Write-Info "Found executable file: $execFile" }
                }
            }
        }
        
        # Check Python requirements
        if ($yamlContent.exec -and $yamlContent.exec[0] -eq "python") {
            $requirementsFile = Join-Path $pluginDir "requirements.txt"
            if (Test-Path $requirementsFile) {
                if ($Verbose) { Write-Info "Found requirements.txt" }
            } else {
                $result.Warnings += "Python plugin should include requirements.txt"
            }
        }
        
        # Check for README
        $readmeFiles = @("README.md", "readme.md", "README.txt", "readme.txt")
        $hasReadme = $false
        foreach ($readmeFile in $readmeFiles) {
            if (Test-Path (Join-Path $pluginDir $readmeFile)) {
                $hasReadme = $true
                if ($Verbose) { Write-Info "Found documentation: $readmeFile" }
                break
            }
        }
        if (-not $hasReadme) {
            $result.Warnings += "Plugin should include README documentation"
        }
        
    } catch {
        $result.Errors += "Error checking file structure: $($_.Exception.Message)"
        $result.Success = $false
    }
    
    return $result
}

function Invoke-PluginSpecificValidation {
    param(
        [string]$Path,
        [bool]$Verbose
    )
    
    $result = @{
        Success = $true
        Errors = @()
        Warnings = @()
        PluginType = "Unknown"
    }
    
    try {
        $targetPath = Resolve-Path $Path
        
        # Determine plugin type
        if ((Get-Item $targetPath).PSIsContainer) {
            $pluginName = Split-Path $targetPath -Leaf
        } else {
            $yamlContent = Get-Content $targetPath -Raw | ConvertFrom-Yaml -ErrorAction SilentlyContinue
            $pluginName = if ($yamlContent -and $yamlContent.name) { $yamlContent.name } else { "Unknown" }
        }
        
        $result.PluginType = $pluginName
        
        # PerformerSiteSync specific validation
        if ($pluginName -eq "PerformerSiteSync" -or $targetPath -like "*PerformerSiteSync*") {
            $performerSyncResult = Test-PerformerSiteSyncPlugin -Path $targetPath -Verbose:$Verbose
            if (-not $performerSyncResult.Success) {
                $result.Success = $false
                $result.Errors += $performerSyncResult.Errors
            }
            $result.Warnings += $performerSyncResult.Warnings
        } else {
            $result.Warnings += "No specific validation rules for plugin type: $pluginName"
        }
        
        if ($result.Success) {
            Write-Success "Plugin-specific validation passed"
        } else {
            Write-Error-Custom "Plugin-specific validation failed"
        }
        
    } catch {
        $result.Errors += "Plugin-specific validation error: $($_.Exception.Message)"
        $result.Success = $false
        Write-Error-Custom "Plugin-specific validation error: $($_.Exception.Message)"
    }
    
    return $result
}

function Test-PerformerSiteSyncPlugin {
    param(
        [string]$Path,
        [bool]$Verbose
    )
    
    $result = @{
        Success = $true
        Errors = @()
        Warnings = @()
    }
    
    try {
        $pluginDir = if ((Get-Item $Path).PSIsContainer) { $Path } else { Split-Path $Path -Parent }
        
        # Check for required Python files
        $requiredFiles = @(
            "performer_site_sync.py",
            "requirements.txt"
        )
        
        foreach ($file in $requiredFiles) {
            $filePath = Join-Path $pluginDir $file
            if (-not (Test-Path $filePath)) {
                $result.Errors += "Required file missing: $file"
                $result.Success = $false
            } else {
                if ($Verbose) { Write-Info "Found required file: $file" }
            }
        }
        
        # Check for modules directory
        $modulesDir = Join-Path $pluginDir "modules"
        if (-not (Test-Path $modulesDir)) {
            $result.Errors += "Modules directory missing"
            $result.Success = $false
        } else {
            if ($Verbose) { Write-Info "Found modules directory" }
            
            # Check for required modules
            $requiredModules = @(
                "__init__.py",
                "config.py",
                "graphql_client.py",
                "performer_sync.py",
                "favorite_performers.py",
                "favorite_sites.py",
                "utils.py"
            )
            
            foreach ($module in $requiredModules) {
                $modulePath = Join-Path $modulesDir $module
                if (-not (Test-Path $modulePath)) {
                    $result.Warnings += "Recommended module missing: $module"
                } else {
                    if ($Verbose) { Write-Info "Found module: $module" }
                }
            }
        }
        
        # Check for UI enhancement file
        $jsFile = Join-Path $pluginDir "performer_site_sync.js"
        if (Test-Path $jsFile) {
            if ($Verbose) { Write-Info "Found UI enhancement file" }
        } else {
            $result.Warnings += "UI enhancement file (performer_site_sync.js) not found"
        }
        
    } catch {
        $result.Errors += "PerformerSiteSync validation error: $($_.Exception.Message)"
        $result.Success = $false
    }
    
    return $result
}

# Helper function to parse YAML (simple implementation)
function ConvertFrom-Yaml {
    param(
        [Parameter(ValueFromPipeline)]
        [string]$InputObject
    )
    
    # This is a very basic YAML parser - for production use, consider using a proper YAML module
    # For now, we'll just return a basic object structure that works for our validation needs
    try {
        # Try to use PowerShell-Yaml module if available
        if (Get-Module -ListAvailable -Name powershell-yaml) {
            Import-Module powershell-yaml
            return ConvertFrom-Yaml $InputObject
        }
        
        # Fallback: very basic parsing
        $lines = $InputObject -split "`n"
        $result = @{}
        
        foreach ($line in $lines) {
            if ($line -match "^(\w+):\s*(.*)$") {
                $key = $matches[1]
                $value = $matches[2].Trim()
                
                # Handle quoted strings
                if ($value -match '^"(.*)"$' -or $value -match "^'(.*)'$") {
                    $value = $matches[1]
                }
                
                $result[$key] = $value
            }
        }
        
        return $result
    } catch {
        return $null
    }
}

# Main execution
try {
    $validationResults = Invoke-PluginValidation -TargetPath $Path -IsVerbose:$Verbose -ContinueOnErrors:$ContinueOnError -AllowDeprecatedFeatures:$AllowDeprecated -CIMode:$CI
    
    if ($CI) {
        if ($validationResults.OverallSuccess) {
            exit 0
        } else {
            exit 1
        }
    }
} catch {
    Write-Error-Custom "Validation script failed: $($_.Exception.Message)"
    if ($CI) {
        exit 1
    }
}
