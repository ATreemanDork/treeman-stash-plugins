#!/usr/bin/env pwsh
# Build script for creating plugin packages and updating index.yml
param(
    [Parameter(Mandatory=$false)]
    [string]$Version = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Plugin = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$All = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$UpdateIndex = $false
)

# Set error handling
$ErrorActionPreference = "Stop"

# Helper functions
function Write-Status {
    param([string]$Message, [string]$Color = "Green")
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor $Color
}

function Get-NextVersion {
    param([string]$CurrentVersion)
    
    if (-not $CurrentVersion -or $CurrentVersion -eq "") {
        return "1.0.0"
    }
    
    $parts = $CurrentVersion.Split('.')
    if ($parts.Length -ne 3) {
        return "1.0.0"
    }
    
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    $patch = [int]$parts[2]
    
    # Auto-increment patch version
    $patch++
    
    return "$major.$minor.$patch"
}

function Get-FileHash-SHA256 {
    param([string]$FilePath)
    return (Get-FileHash -Path $FilePath -Algorithm SHA256).Hash.ToLower()
}

function Build-Plugin {
    param(
        [string]$PluginName,
        [string]$PluginVersion
    )
    
    Write-Status "Building plugin: $PluginName v$PluginVersion"
    
    $pluginDir = Join-Path $PSScriptRoot $PluginName
    $distDir = Join-Path $PSScriptRoot "dist"
    $packageName = "$PluginName-$PluginVersion.zip"
    $packagePath = Join-Path $distDir $packageName
    
    if (-not (Test-Path $pluginDir)) {
        throw "Plugin directory not found: $pluginDir"
    }
    
    # Create dist directory if it doesn't exist
    if (-not (Test-Path $distDir)) {
        New-Item -ItemType Directory -Path $distDir -Force | Out-Null
    }
    
    # Remove old package if exists
    if (Test-Path $packagePath) {
        Remove-Item $packagePath -Force
    }
    
    # Create temporary directory for packaging
    $tempDir = Join-Path $env:TEMP "stash-plugin-build-$(Get-Random)"
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    
    try {
        # Copy plugin files to temp directory
        $tempPluginDir = Join-Path $tempDir $PluginName
        Copy-Item -Path $pluginDir -Destination $tempPluginDir -Recurse -Force
        
        # Remove development files that shouldn't be in the package
        $excludePatterns = @(
            "*.pyc",
            "__pycache__",
            ".pytest_cache",
            "*.log",
            ".env",
            ".env.local",
            "node_modules",
            ".git*",
            "*.tmp",
            "*.temp"
        )
        
        foreach ($pattern in $excludePatterns) {
            Get-ChildItem -Path $tempPluginDir -Recurse -Name $pattern -Force | ForEach-Object {
                $itemPath = Join-Path $tempPluginDir $_
                if (Test-Path $itemPath) {
                    Remove-Item $itemPath -Recurse -Force
                }
            }
        }
        
        # Create the ZIP package
        Write-Status "Creating package: $packageName"
        Compress-Archive -Path $tempPluginDir -DestinationPath $packagePath -CompressionLevel Optimal -Force
        
        # Calculate SHA256
        $sha256 = Get-FileHash-SHA256 -FilePath $packagePath
        $packageSize = (Get-Item $packagePath).Length
        
        Write-Status "Package created successfully:"
        Write-Status "  File: $packageName" -Color "Cyan"
        Write-Status "  Size: $([math]::Round($packageSize / 1KB, 2)) KB" -Color "Cyan"
        Write-Status "  SHA256: $sha256" -Color "Cyan"
        
        return @{
            Name = $packageName
            Path = $packagePath
            SHA256 = $sha256
            Size = $packageSize
            Plugin = $PluginName
            Version = $PluginVersion
        }
    }
    finally {
        # Clean up temp directory
        if (Test-Path $tempDir) {
            Remove-Item $tempDir -Recurse -Force
        }
    }
}

function Update-IndexYml {
    param([array]$Packages)
    
    Write-Status "Updating index.yml"
    
    $indexPath = Join-Path $PSScriptRoot "index.yml"
    $currentDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    # Load current index or create new
    if (Test-Path $indexPath) {
        $indexContent = Get-Content $indexPath -Raw
    } else {
        $indexContent = "# Treeman's Stash Plugins Repository`n# Source URL for Stash Plugin Manager: https://atreemandork.github.io/index.yml`n`n"
    }
    
    # Parse existing entries (simple approach for this use case)
    $entries = @()
    
    foreach ($package in $Packages) {
        $pluginId = $package.Plugin.ToLower() -replace '[^a-z0-9]', '-'
        $downloadUrl = "https://github.com/ATreemanDork/treeman-stash-plugins/releases/download/v$($package.Version)/$($package.Name)"
        
        # Read plugin YAML for metadata
        $pluginYamlPath = Join-Path $PSScriptRoot "$($package.Plugin)" "$($package.Plugin.ToLower() -replace '[^a-z0-9_]', '_').yml"
        if (-not (Test-Path $pluginYamlPath)) {
            $pluginYamlPath = Join-Path $PSScriptRoot "$($package.Plugin)" "$($package.Plugin -replace '[^a-zA-Z0-9_]', '_').yml"
        }
        
        $pluginName = $package.Plugin
        $pluginDescription = "Advanced Stash plugin"
        
        if (Test-Path $pluginYamlPath) {
            $yamlContent = Get-Content $pluginYamlPath -Raw
            if ($yamlContent -match "name:\s*(.+)") {
                $pluginName = $matches[1].Trim()
            }
            if ($yamlContent -match "description:\s*(.+)") {
                $pluginDescription = $matches[1].Trim()
            }
        }
        
        $entry = @"
- id: $pluginId
  name: $pluginName
  metadata:
    description: $pluginDescription
  version: $($package.Version)
  date: $currentDate
  path: plugins/$($package.Name)
  sha256: $($package.SHA256)
  requires: []
"@
        $entries += $entry
    }
    
    # Create new index content
    $newIndexContent = @"
# Treeman's Stash Plugins Repository
# Source URL for Stash Plugin Manager: https://atreemandork.github.io/index.yml

$($entries -join "`n")
"@
    
    # Write to file
    Set-Content -Path $indexPath -Value $newIndexContent -Encoding UTF8
    Write-Status "index.yml updated successfully"
}

# Main execution
try {
    Write-Status "Starting plugin build process" -Color "Yellow"
    
    # Determine which plugins to build
    $pluginsToBuild = @()
    
    if ($Plugin) {
        $pluginsToBuild += $Plugin
    } elseif ($All) {
        # Find all plugin directories
        $pluginDirs = Get-ChildItem -Path $PSScriptRoot -Directory | Where-Object { 
            $_.Name -notmatch "^(\.|_|dist|references|validator|docs|\.git|\.vscode|\.github).*" -and
            (Test-Path (Join-Path $_.FullName "*.yml"))
        }
        $pluginsToBuild = $pluginDirs.Name
    } else {
        # Default to PerformerSiteSync
        $pluginsToBuild += "PerformerSiteSync"
    }
    
    if ($pluginsToBuild.Count -eq 0) {
        throw "No plugins found to build"
    }
    
    Write-Status "Building plugins: $($pluginsToBuild -join ', ')" -Color "Cyan"
    
    # Build packages
    $packages = @()
    foreach ($pluginName in $pluginsToBuild) {
        # Determine version
        $pluginVersion = $Version
        if (-not $pluginVersion) {
            # Try to get version from plugin YAML
            $yamlFiles = Get-ChildItem -Path (Join-Path $PSScriptRoot $pluginName) -Filter "*.yml"
            if ($yamlFiles.Count -gt 0) {
                $yamlContent = Get-Content $yamlFiles[0].FullName -Raw
                if ($yamlContent -match "version:\s*([^\r\n]+)") {
                    $pluginVersion = $matches[1].Trim()
                }
            }
            
            if (-not $pluginVersion) {
                $pluginVersion = "1.0.0"
            }
        }
        
        $package = Build-Plugin -PluginName $pluginName -PluginVersion $pluginVersion
        $packages += $package
    }
    
    # Update index.yml if requested
    if ($UpdateIndex -or $All) {
        Update-IndexYml -Packages $packages
    }
    
    Write-Status "Build process completed successfully!" -Color "Green"
    Write-Status "Packages created:" -Color "Yellow"
    foreach ($package in $packages) {
        Write-Status "  - $($package.Name)" -Color "Cyan"
    }
    
    if ($UpdateIndex -or $All) {
        Write-Status "`nNext steps:" -Color "Yellow"
        Write-Status "1. Commit and push the updated index.yml to your repository" -Color "Cyan"
        Write-Status "2. Create a GitHub release with the generated ZIP files" -Color "Cyan"
        Write-Status "3. Add the source URL to Stash: https://atreemandork.github.io/index.yml" -Color "Cyan"
    }
}
catch {
    Write-Status "Build failed: $($_.Exception.Message)" -Color "Red"
    exit 1
}
