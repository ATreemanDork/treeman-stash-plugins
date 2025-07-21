# Stash Plugin Integration Guide

This document explains how the Stash plugin integration works in this repository, enabling users to install plugins directly through Stash's built-in plugin manager.

## 🏗️ Architecture Overview

### Components

1. **Plugin Source Index** (`index.yml`)
   - YAML file listing all available plugins
   - Hosted at `https://atreemandork.github.io/index.yml`
   - Contains metadata, download URLs, and SHA256 checksums

2. **Build System** (`build-plugins.ps1`)
   - Creates ZIP packages for each plugin
   - Generates SHA256 checksums
   - Updates the source index automatically

3. **Automated Release** (`.github/workflows/release.yml`)
   - Triggers on pushes to main branch
   - Auto-increments version numbers
   - Creates GitHub releases with plugin packages
   - Deploys index.yml to GitHub Pages

4. **GitHub Pages Hosting**
   - Serves the index.yml file
   - Configured via `_config.yml`
   - Accessible to Stash plugin manager

## 🔄 Workflow Process

### Development to Release

1. **Development**
   - Make changes to plugin code
   - Update plugin documentation
   - Run validation: `./validate_all.ps1`

2. **Commit & Push**
   - Commit changes to main branch
   - GitHub Actions automatically triggers

3. **Automated Release**
   - Determines next version number
   - Updates plugin YAML files with new version
   - Builds plugin packages (ZIP files)
   - Calculates SHA256 checksums
   - Updates index.yml
   - Creates GitHub release
   - Deploys to GitHub Pages

4. **User Installation**
   - Users add source URL to Stash
   - Install plugins through Stash UI
   - Automatic updates available

### Manual Release Process

If you need to manually trigger a release:

```bash
# Build specific plugin
.\build-plugins.ps1 -Plugin "PerformerSiteSync" -Version "1.2.0" -UpdateIndex

# Build all plugins
.\build-plugins.ps1 -All -Version "1.2.0" -UpdateIndex

# Create GitHub release manually (or use GitHub Actions)
```

## 📋 Plugin Source Format

The `index.yml` follows Stash's plugin source specification:

```yaml
- id: plugin-id                    # Unique identifier
  name: Plugin Name               # Display name
  version: 1.0.0                 # Semantic version
  date: 2025-01-20               # Release date
  requires: []                   # Dependencies (plugin IDs)
  path: https://github.com/.../plugin.zip  # Download URL
  sha256: abc123...              # File checksum
  metadata:                      # Additional metadata
    author: Author Name
    description: Plugin description
    homepage: https://github.com/...
    license: AGPL-3.0
    tags:
      - tag1
      - tag2
    python_version: ">=3.8"
    stash_version: ">=0.20.0"
```

## 🎯 User Installation

### Method 1: Stash Plugin Manager (Recommended)

1. Open Stash → Settings → Plugins
2. In "Available Plugins" section, click "Add Source"
3. Enter: `https://atreemandork.github.io/index.yml`
4. Click "Add"
5. Install plugins from the "Available Plugins" list

### Method 2: Manual Installation

1. Download ZIP from GitHub Releases
2. Extract to Stash plugins directory
3. Restart Stash
4. Enable plugin in Settings → Plugins

## 🔧 Configuration

### Plugin Settings

All plugins support configuration through Stash UI:
- Go to Settings → Plugins → [Plugin Name] → Plugin Settings
- Settings are defined in the plugin YAML file
- Changes take effect immediately

### External API Setup

For plugins requiring external APIs:
1. Go to Settings → Metadata Providers → Stash-boxes
2. Add endpoints for StashDB, ThePornDB, FansDB
3. Configure API keys and display names

## 🧪 Testing & Validation

### Local Testing

```bash
# Test validation
.\test-integration.ps1 -TestValidation

# Test build process
.\test-integration.ps1 -TestBuild

# Test everything
.\test-integration.ps1 -All
```

### VS Code Integration

Use built-in tasks:
1. **Ctrl+Shift+P** → "Tasks: Run Task"
2. Select from available tasks:
   - Validate All Plugins
   - Build Plugin Package
   - Test Integration

## 🚀 Adding New Plugins

### Using Template

```bash
.\new-plugin.ps1 -Name "MyPlugin" -Description "What it does" -Author "Your Name" -Type "python"
```

### Manual Creation

1. Create plugin directory
2. Add plugin YAML manifest
3. Implement plugin functionality
4. Add to build system
5. Update documentation

### Release Requirements

- Valid plugin YAML configuration
- Complete README.md documentation
- Working validation tests
- Proper error handling
- Version compatibility info

## 🔍 Troubleshooting

### Common Issues

**Plugin not appearing in Stash**
- Check source URL is correctly added
- Verify GitHub Pages is serving index.yml
- Check plugin YAML syntax

**Build failures**
- Run validation first: `./validate_all.ps1`
- Check for syntax errors
- Verify all required files present

**Version conflicts**
- Use semantic versioning
- Don't manually edit version numbers
- Let automation handle versioning

### Debugging

```bash
# Validate specific plugin
.\validate.bat PerformerSiteSync

# Check build output
.\build-plugins.ps1 -Plugin "PerformerSiteSync" -Verbose

# Test plugin in isolation
cd PerformerSiteSync
python performer_site_sync.py
```

## 📚 Resources

- [Stash Plugin Documentation](https://docs.stashapp.cc/plugins/plugins)
- [Stash Plugin Manager Guide](https://docs.stashapp.cc/in-app-manual/plugins/)
- [Plugin Development Best Practices](https://github.com/stashapp/CommunityScripts)
- [Semantic Versioning](https://semver.org/)

## 🔧 Advanced Configuration

### Custom Source Hosting

To host your own plugin source:

1. Fork this repository
2. Update URLs in `index.yml` and workflows
3. Enable GitHub Pages for your fork
4. Users add your GitHub Pages URL as source

### Multiple Version Support

For backward compatibility:

1. Create separate index files per Stash version
2. Update GitHub Actions to build multiple versions
3. Host different sources for stable/develop branches

### Enterprise Deployment

For private/enterprise use:

1. Host index.yml on internal web server
2. Modify download URLs to point to internal releases
3. Add authentication if required
4. Configure Stash to use internal source URL

---

**This integration makes plugin installation as easy as installing browser extensions or VS Code plugins!**
