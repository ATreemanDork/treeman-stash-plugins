#!/usr/bin/env pwsh
# Test script for plugin build and release process

param(
    [Parameter(Mandatory=$false)]
    [switch]$TestBuild = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$TestValidation = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$All = $false
)

$ErrorActionPreference = "Stop"

function Write-TestStatus {
    param([string]$Message, [string]$Color = "Green")
    Write-Host "[TEST] $Message" -ForegroundColor $Color
}

function Test-BuildProcess {
    Write-TestStatus "Testing plugin build process..." -Color "Yellow"
    
    try {
        # Test build script
        ./build-plugins.ps1 -Plugin "PerformerSiteSync" -Version "1.0.0-test" -UpdateIndex
        
        # Check if files were created
        $expectedFiles = @(
            "dist/PerformerSiteSync-1.0.0-test.zip",
            "index.yml"
        )
        
        foreach ($file in $expectedFiles) {
            if (Test-Path $file) {
                Write-TestStatus "✅ Created: $file" -Color "Green"
            } else {
                throw "Missing expected file: $file"
            }
        }
        
        # Validate ZIP contents
        $zipPath = "dist/PerformerSiteSync-1.0.0-test.zip"
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
        
        $expectedEntries = @(
            "PerformerSiteSync/performer_site_sync.yml",
            "PerformerSiteSync/performer_site_sync.py",
            "PerformerSiteSync/requirements.txt",
            "PerformerSiteSync/README.md"
        )
        
        foreach ($entry in $expectedEntries) {
            $found = $zip.Entries | Where-Object { $_.FullName -eq $entry }
            if ($found) {
                Write-TestStatus "✅ ZIP contains: $entry" -Color "Green"
            } else {
                throw "ZIP missing expected entry: $entry"
            }
        }
        
        $zip.Dispose()
        
        Write-TestStatus "✅ Build process test passed!" -Color "Green"
        
    } catch {
        Write-TestStatus "❌ Build process test failed: $($_.Exception.Message)" -Color "Red"
        throw
    } finally {
        # Clean up test files
        if (Test-Path "dist/PerformerSiteSync-1.0.0-test.zip") {
            Remove-Item "dist/PerformerSiteSync-1.0.0-test.zip" -Force
        }
    }
}

function Test-ValidationProcess {
    Write-TestStatus "Testing validation process..." -Color "Yellow"
    
    try {
        # Test comprehensive validation
        ./validate_all.ps1 -Verbose
        
        if ($LASTEXITCODE -eq 0) {
            Write-TestStatus "✅ Validation process test passed!" -Color "Green"
        } else {
            throw "Validation failed with exit code: $LASTEXITCODE"
        }
        
    } catch {
        Write-TestStatus "❌ Validation process test failed: $($_.Exception.Message)" -Color "Red"
        throw
    }
}

function Test-IndexYmlStructure {
    Write-TestStatus "Testing index.yml structure..." -Color "Yellow"
    
    try {
        if (-not (Test-Path "index.yml")) {
            throw "index.yml not found"
        }
        
        $content = Get-Content "index.yml" -Raw
        
        # Check for required YAML structure
        $requiredPatterns = @(
            "id:\s*\w+",
            "name:\s*.+",
            "version:\s*\d+\.\d+\.\d+",
            "date:\s*\d{4}-\d{2}-\d{2}",
            "path:\s*https?://.+",
            "sha256:\s*[a-f0-9]*"
        )
        
        foreach ($pattern in $requiredPatterns) {
            if ($content -match $pattern) {
                Write-TestStatus "✅ Found pattern: $pattern" -Color "Green"
            } else {
                Write-TestStatus "⚠️  Missing pattern: $pattern" -Color "Yellow"
            }
        }
        
        Write-TestStatus "✅ index.yml structure test completed!" -Color "Green"
        
    } catch {
        Write-TestStatus "❌ index.yml structure test failed: $($_.Exception.Message)" -Color "Red"
        throw
    }
}

# Main execution
try {
    Write-TestStatus "Starting Stash plugin integration tests..." -Color "Cyan"
    
    if ($TestValidation -or $All) {
        Test-ValidationProcess
        Write-TestStatus ""
    }
    
    if ($TestBuild -or $All) {
        Test-BuildProcess
        Write-TestStatus ""
    }
    
    Test-IndexYmlStructure
    
    Write-TestStatus "🎉 All tests passed successfully!" -Color "Green"
    Write-TestStatus ""
    Write-TestStatus "📋 Integration Ready:" -Color "Yellow"
    Write-TestStatus "1. Commit and push changes to trigger release workflow" -Color "Cyan"
    Write-TestStatus "2. GitHub Pages will serve index.yml at: https://atreemandork.github.io/index.yml" -Color "Cyan"
    Write-TestStatus "3. Users can add this URL to Stash Plugin Manager" -Color "Cyan"
    
} catch {
    Write-TestStatus "❌ Test suite failed: $($_.Exception.Message)" -Color "Red"
    exit 1
}
