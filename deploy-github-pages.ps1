# Deploy to GitHub Pages
# This script deploys the plugin index and packages to ATreemanDork.github.io

param(
    [string]$GitHubPagesPath = "",
    [switch]$DryRun,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

function Test-GitHubPagesRepo {
    param([string]$Path)
    
    if (-not (Test-Path $Path)) {
        throw "GitHub Pages repository path does not exist: $Path"
    }
    
    $gitDir = Join-Path $Path ".git"
    if (-not (Test-Path $gitDir)) {
        throw "Path is not a git repository: $Path"
    }
    
    # Check if it's the correct repository
    $remoteUrl = git -C $Path remote get-url origin 2>$null
    if ($remoteUrl -notmatch "ATreemanDork\.github\.io") {
        Write-Warning "Repository URL doesn't match expected GitHub Pages repo: $remoteUrl"
    }
    
    return $true
}

function Copy-PluginFiles {
    param(
        [string]$SourcePath,
        [string]$DestPath,
        [switch]$DryRun
    )
    
    # Files to deploy
    $filesToDeploy = @(
        @{
            Source = "index.yml"
            Dest = "index.yml"
            Required = $true
        },
        @{
            Source = "dist\*.zip"
            Dest = "plugins\"
            Required = $false
        }
    )
    
    foreach ($file in $filesToDeploy) {
        $sourcePath = Join-Path $SourcePath $file.Source
        $destPath = Join-Path $DestPath $file.Dest
        
        if ($file.Source -like "*\*") {
            # Handle wildcard patterns
            $sourceFiles = Get-ChildItem -Path $sourcePath -ErrorAction SilentlyContinue
            if ($sourceFiles) {
                # Ensure destination directory exists
                $destDir = Split-Path $destPath -Parent
                if ($destDir -and -not (Test-Path $destDir)) {
                    Write-Log "Creating directory: $destDir"
                    if (-not $DryRun) {
                        New-Item -Path $destDir -ItemType Directory -Force | Out-Null
                    }
                }
                
                foreach ($sourceFile in $sourceFiles) {
                    $finalDest = Join-Path $destPath $sourceFile.Name
                    Write-Log "Copying: $($sourceFile.FullName) -> $finalDest"
                    if (-not $DryRun) {
                        Copy-Item -Path $sourceFile.FullName -Destination $finalDest -Force
                    }
                }
            } elseif ($file.Required) {
                throw "Required file pattern not found: $sourcePath"
            }
        } else {
            # Handle single files
            if (Test-Path $sourcePath) {
                Write-Log "Copying: $sourcePath -> $destPath"
                if (-not $DryRun) {
                    $destDir = Split-Path $destPath -Parent
                    if ($destDir -and -not (Test-Path $destDir)) {
                        New-Item -Path $destDir -ItemType Directory -Force | Out-Null
                    }
                    Copy-Item -Path $sourcePath -Destination $destPath -Force
                }
            } elseif ($file.Required) {
                throw "Required file not found: $sourcePath"
            }
        }
    }
}

function Update-GitHubPages {
    param(
        [string]$GitHubPagesPath,
        [switch]$DryRun
    )
    
    Push-Location $GitHubPagesPath
    try {
        # Check git status
        $gitStatus = git status --porcelain
        if ($gitStatus) {
            Write-Log "Changes detected in GitHub Pages repository:"
            $gitStatus | ForEach-Object { Write-Log "  $_" }
            
            if (-not $DryRun) {
                # Add all changes
                Write-Log "Adding changes to git..."
                git add .
                
                # Commit with timestamp
                $commitMessage = "Update Stash plugins - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
                Write-Log "Committing: $commitMessage"
                git commit -m $commitMessage
                
                # Push to GitHub
                Write-Log "Pushing to GitHub Pages..."
                git push origin main
                
                Write-Log "✅ Successfully deployed to GitHub Pages!"
                Write-Log "🌐 Plugin source will be available at: https://atreemandork.github.io/index.yml"
            } else {
                Write-Log "[DRY RUN] Would commit and push changes"
            }
        } else {
            Write-Log "No changes detected in GitHub Pages repository"
        }
    }
    finally {
        Pop-Location
    }
}

# Main execution
try {
    Write-Log "Starting GitHub Pages deployment"
    
    # Validate parameters
    if (-not $GitHubPagesPath) {
        # Try to auto-detect
        $possiblePaths = @(
            "C:\Users\$env:USERNAME\OneDrive\Documents\GitHub\ATreemanDork.github.io",
            "C:\Users\$env:USERNAME\Documents\GitHub\ATreemanDork.github.io",
            "..\ATreemanDork.github.io"
        )
        
        foreach ($path in $possiblePaths) {
            if (Test-Path $path) {
                $GitHubPagesPath = $path
                Write-Log "Auto-detected GitHub Pages repository: $GitHubPagesPath"
                break
            }
        }
        
        if (-not $GitHubPagesPath) {
            throw "GitHub Pages repository path not specified and could not be auto-detected. Use -GitHubPagesPath parameter."
        }
    }
    
    # Validate GitHub Pages repository
    Test-GitHubPagesRepo -Path $GitHubPagesPath
    Write-Log "✅ GitHub Pages repository validated: $GitHubPagesPath"
    
    # Build plugins first
    Write-Log "Building plugins..."
    if (-not $DryRun) {
        & .\build-plugins.ps1
        if ($LASTEXITCODE -ne 0) {
            throw "Plugin build failed"
        }
    } else {
        Write-Log "[DRY RUN] Would build plugins"
    }
    
    # Copy files to GitHub Pages repository
    Write-Log "Copying files to GitHub Pages repository..."
    Copy-PluginFiles -SourcePath $PWD -DestPath $GitHubPagesPath -DryRun:$DryRun
    
    # Update GitHub Pages repository
    Write-Log "Updating GitHub Pages repository..."
    Update-GitHubPages -GitHubPagesPath $GitHubPagesPath -DryRun:$DryRun
    
    Write-Log "🎉 Deployment completed successfully!"
    
    if (-not $DryRun) {
        Write-Log ""
        Write-Log "📋 Next steps:"
        Write-Log "1. Verify deployment at: https://atreemandork.github.io/index.yml"
        Write-Log "2. Test in Stash Plugin Manager with source URL: https://atreemandork.github.io/index.yml"
        Write-Log "3. Plugin ZIP files are available at: https://atreemandork.github.io/plugins/"
    }
}
catch {
    Write-Log "❌ Deployment failed: $($_.Exception.Message)" -Level "ERROR"
    exit 1
}
