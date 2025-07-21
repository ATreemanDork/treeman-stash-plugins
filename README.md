# Treeman's Stash Plugins

A collection of advanced plugins for the [Stash](https://github.com/stashapp/stash) adult media organizer, featuring sophisticated performer and site synchronization capabilities with built-in validation tools.

## 🚀 Features

- **Performer/Site Sync**: Comprehensive synchronization between your local Stash instance and external databases (StashDB, ThePornDB, FansDB)
- **Plugin Validation**: Automated validation tools to ensure plugin configurations meet Stash standards
- **Modular Architecture**: Clean, maintainable code structure with separate concerns
- **Comprehensive Documentation**: Detailed setup and usage instructions

## 📦 Available Plugins

| Plugin | Version | Description | Status |
|--------|---------|-------------|--------|
| [**PerformerSiteSync**](PerformerSiteSync/) | v1.0.0 | Multi-source performer & site synchronization | ✅ Stable |

### PerformerSiteSync
> **Comprehensive performer and site data synchronization**

Synchronize performer and site data between your local Stash instance and multiple external databases including StashDB, ThePornDB, and FansDB.

**🔥 Key Features:**
- **Multi-Source Sync**: StashDB, ThePornDB, FansDB integration
- **Intelligent Caching**: Configurable expiration with smart invalidation
- **Rate Limiting**: Prevents API abuse and rate limit violations
- **Manual Controls**: Enhanced UI with granular task management
- **Favorite Import**: Import performers and sites from external sources
- **Auto-Creation**: Automatically create missing entities
- **Error Recovery**: Comprehensive error handling and retry logic
- **Progress Tracking**: Real-time updates for long-running operations

**📋 Requirements:** Python 3.8+, External API keys  
**🎯 Use Case:** Large libraries needing automated metadata synchronization

[**📖 Full Documentation**](PerformerSiteSync/README.md) • [**⚙️ Configuration Guide**](PerformerSiteSync/README.md#configuration) • [**🐛 Troubleshooting**](PerformerSiteSync/README.md#troubleshooting)

---

### Coming Soon
> **Future plugins in development**

- **🎬 Scene Enhancer**: Advanced scene metadata and organization tools
- **🏷️ Smart Tagger**: AI-powered automatic tagging system  
- **📊 Analytics Dashboard**: Comprehensive library statistics and insights
- **🔍 Advanced Search**: Enhanced search capabilities with filters
- **🎨 Theme Manager**: Custom themes and UI customization tools

*Have an idea for a plugin? [Open an issue](https://github.com/ATreemanDork/treeman-stash-plugins/issues/new) to suggest it!*

## 🛠️ Development Tools

### Plugin Validator
Automated validation tools to ensure your Stash plugins meet community standards and work correctly.

### Plugin Template & Generator
Streamlined plugin creation with pre-configured templates and automated setup.

**Create New Plugin:**
```bash
# Interactive plugin creation
.\new-plugin.ps1 -Name "YourPlugin" -Description "What it does" -Author "Your Name" -Type "python"

# Types available: python, javascript, mixed
```

**Features:**
- **JSON Schema Validation**: Validates plugin YAML files against the official Stash plugin schema
- **Comprehensive Error Reporting**: Detailed error messages with suggestions for fixes
- **Multiple Validation Modes**: Support for single files, directories, or entire workspaces
- **CI/CD Integration**: Exit codes suitable for continuous integration pipelines
- **Cross-Platform**: Works on Windows, macOS, and Linux

**Quick Start:**
```bash
# Windows
.\validate.bat PerformerSiteSync

# Linux/macOS
./validate.sh PerformerSiteSync

# PowerShell (all platforms)
pwsh -File .\validate_all.ps1 -Path PerformerSiteSync -Verbose
```

**Node.js Validator (Advanced):**
```bash
# Install dependencies
cd validator
npm install

# Validate all plugins in the workspace
npm run main

# Validate specific plugin
npm run main ../PerformerSiteSync/performer_site_sync.yml

# Enable verbose output
npm run main -- -v

# Allow deprecated features
npm run main -- -d

# Continue on errors (don't stop at first error)
npm run main -- -a
```

**Python Validator (Configuration-focused):**
```bash
# Install dependencies
pip install -r requirements-dev.txt

# Validate plugins
python validate_plugins.py              # Basic validation
python validate_plugins.py --verbose    # Detailed output
python validate_plugins.py --ci         # CI mode with exit codes
```

**Command Line Options:**
- `-v, --verbose`: Verbose output showing validation status for all files
- `-d, --allow-deprecated`: Allow deprecated features in plugin configurations
- `-a, --continue-on-error`: Continue validation even after encountering errors
- `--ci`: Exit with appropriate code for CI/CD systems

**VS Code Integration:**
Use the built-in tasks for quick validation:
1. **Ctrl+Shift+P** → "Tasks: Run Task"
2. Select "Validate All Plugins" or "Validate PerformerSiteSync"

## 📋 Installation

### Option 1: Stash Plugin Manager (Recommended)

The easiest way to install these plugins is through Stash's built-in plugin manager:

1. **Open Stash Settings**
   - Go to **Settings → Plugins**

2. **Add Plugin Source**
   - In the "Available Plugins" section, click "Add Source"
   - Enter source URL: `https://atreemandork.github.io/index.yml`
   - Click "Add"

3. **Install Plugins**
   - Browse available plugins in the "Available Plugins" section
   - Click "Install" next to the plugins you want
   - Plugins will be automatically downloaded and installed

4. **Enable Plugins**
   - Go to the "Installed Plugins" section
   - Enable the plugins you've installed
   - Configure plugin settings as needed

### Option 2: Manual Installation

If you prefer manual installation or need development access:

#### General Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ATreemanDork/treeman-stash-plugins.git
   cd treeman-stash-plugins
   ```

2. **Choose Your Plugins**
   Browse the [available plugins](#-available-plugins) and select the ones you need.

3. **Install Plugin Dependencies**
   Each plugin may have different requirements:
   ```bash
   # For Python-based plugins (like PerformerSiteSync)
   pip install -r [PluginName]/requirements.txt
   
   # For Node.js-based plugins
   cd [PluginName] && npm install
   ```

4. **Copy to Stash**
   ```bash
   # Copy individual plugin
   cp -r [PluginName] /path/to/stash/plugins/
   
   # Or copy all plugins
   cp -r */ /path/to/stash/plugins/
   ```

5. **Configure in Stash**
   - Go to **Settings → Plugins**
   - Enable the plugins you've installed
   - Configure plugin-specific settings as needed

#### Plugin-Specific Installation

**PerformerSiteSync**
```bash
# Prerequisites: Python 3.8+
pip install -r PerformerSiteSync/requirements.txt

# Copy to Stash plugins directory
cp -r PerformerSiteSync /path/to/stash/plugins/

# Configure external API endpoints in Stash:
# Settings → Metadata Providers → Stash-boxes
```

### Development Setup (Optional)
For contributing or validation:
```bash
# Install validation tools
cd validator && npm install

# Install development dependencies
pip install -r requirements-dev.txt
```

## 🔧 Configuration

### General Requirements
- **Stash**: v0.20.0 or later
- **Platform**: Windows, macOS, or Linux

### Plugin-Specific Requirements

| Plugin | Language | Version | Dependencies |
|--------|----------|---------|--------------|
| PerformerSiteSync | Python | 3.8+ | requests, stashapi-tools |
| *Future plugins* | Various | TBD | Plugin-specific |

### External API Configuration

Some plugins require external API access. Configure these in Stash:

**Settings → Metadata Providers → Stash-boxes**

#### Supported External Sources
1. **StashDB**: `https://stashdb.org/graphql`
2. **ThePornDB**: `https://theporndb.net/graphql`  
3. **FansDB**: `https://fansdb.cc/graphql`

Each source requires:
- ✅ Valid API endpoint URL
- 🔑 Personal API key
- 🏷️ Display name for identification

### Plugin Settings
After installation, configure each plugin through:
**Settings → Plugins → [Plugin Name] → Plugin Settings**

Common settings across plugins:
- **Cache Expiration**: Data refresh intervals
- **Rate Limiting**: API request throttling
- **Debug Logging**: Troubleshooting information
- **Auto-Features**: Automatic entity creation/updates

## 🧪 Validation & Quality Assurance

This repository includes comprehensive validation tools to ensure all plugins meet high quality standards:

### Quick Validation
```bash
# Validate all plugins
.\validate.bat                    # Windows
./validate.sh                     # Linux/macOS  
pwsh -File .\validate_all.ps1     # PowerShell (all platforms)

# Validate specific plugin
.\validate.bat PerformerSiteSync   # Windows
./validate.sh PerformerSiteSync    # Linux/macOS
```

### Multi-Layer Validation
- **📋 Schema Compliance**: YAML structure against Stash plugin standards
- **📁 File Dependencies**: Required files and proper references
- **⚙️ Configuration**: Settings validation and type checking
- **🐍 Code Quality**: Python/JavaScript syntax and import validation
- **📚 Documentation**: README and documentation completeness
- **🔗 API Connectivity**: External service connectivity testing

### Automated Quality Checks
All plugins are automatically validated through:
- **🔄 GitHub Actions**: On every push and pull request
- **⚡ Pre-commit Hooks**: Before code commits (optional)
- **🖥️ VS Code Tasks**: Integrated development workflow
- **🚀 Release Validation**: Before version releases

### Plugin Standards
Each plugin must meet these requirements:
- ✅ Valid YAML configuration following Stash schema
- ✅ Complete documentation with setup instructions
- ✅ Error handling and logging implementation
- ✅ Version compatibility information
- ✅ Dependency management (requirements.txt, package.json, etc.)
- ✅ Test coverage for core functionality *(Coming Soon)*

## 📖 Documentation

### Plugin Documentation
- [**PerformerSiteSync**](PerformerSiteSync/README.md) - Complete setup and usage guide
- [**Plugin Development Guide**](docs/DEVELOPMENT.md) - Creating new plugins *(Coming Soon)*
- [**API Reference**](docs/API.md) - Technical documentation *(Coming Soon)*

### Support & Troubleshooting
- [**Troubleshooting Guide**](docs/TROUBLESHOOTING.md) - Common issues and solutions *(Coming Soon)*
- [**FAQ**](docs/FAQ.md) - Frequently asked questions *(Coming Soon)*
- [**Configuration Examples**](docs/EXAMPLES.md) - Real-world setups *(Coming Soon)*

### Community Resources
- [**Plugin Template**](https://github.com/ATreemanDork/stash-plugin-template) - Boilerplate for new plugins *(Coming Soon)*
- [**Best Practices**](docs/BEST_PRACTICES.md) - Development guidelines *(Coming Soon)*
- [**Contributing Guide**](CONTRIBUTING.md) - How to contribute *(Coming Soon)*

## 🤝 Contributing

We welcome contributions to existing plugins and entirely new plugins! Here's how to get involved:

### Adding a New Plugin

**Quick Start with Template:**
```bash
# Create new plugin from template
.\new-plugin.ps1 -Name "MyAwesomePlugin" -Description "Does awesome things" -Author "Your Name" -Type "python"

# Available types: python, javascript, mixed
```

**Manual Creation:**

1. **Fork & Clone**
   ```bash
   git fork https://github.com/ATreemanDork/treeman-stash-plugins
   git clone your-fork-url
   cd treeman-stash-plugins
   ```

2. **Create Plugin Structure**
   ```bash
   mkdir YourPluginName
   cd YourPluginName
   
   # Required files:
   touch your_plugin_name.yml    # Plugin manifest
   touch README.md               # Documentation
   touch requirements.txt        # Dependencies (if Python)
   # or package.json             # Dependencies (if Node.js)
   ```

3. **Follow Plugin Standards**
   - Use the [validation tools](#-validation--quality-assurance) throughout development
   - Follow [plugin naming conventions](docs/DEVELOPMENT.md#naming-conventions) *(Coming Soon)*
   - Include comprehensive documentation
   - Add proper error handling

4. **Test Thoroughly**
   ```bash
   # Validate your plugin
   .\validate.bat YourPluginName
   
   # Test with actual Stash instance
   # Document any external dependencies
   ```

5. **Submit Pull Request**
   - Create feature branch: `git checkout -b plugin/your-plugin-name`
   - Commit changes: `git commit -m 'Add YourPluginName plugin'`
   - Push to branch: `git push origin plugin/your-plugin-name`
   - Open pull request with detailed description

### Improving Existing Plugins

1. **Identify Enhancement**: Check [existing issues](https://github.com/ATreemanDork/treeman-stash-plugins/issues) or create new ones
2. **Create Feature Branch**: `git checkout -b feature/amazing-enhancement`
3. **Make Changes**: Follow existing code patterns and standards
4. **Validate Changes**: Run full validation suite
5. **Test Compatibility**: Ensure backward compatibility
6. **Update Documentation**: Reflect any changes in READMEs
7. **Submit Pull Request**: Include before/after comparisons

### Development Workflow

```bash
# 1. Set up development environment
npm install                     # Validation tools
pip install -r requirements-dev.txt  # Python tools

# 2. Make your changes
# ...

# 3. Validate everything
pwsh -File .\validate_all.ps1 -Verbose

# 4. Test with Stash
# Install plugin in test Stash instance
# Verify functionality works as expected

# 5. Submit for review
git push origin your-branch
# Open pull request
```

### Plugin Ideas & Requests

Have an idea for a new plugin? We'd love to hear it!

- 🔍 **[Browse existing requests](https://github.com/ATreemanDork/treeman-stash-plugins/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)**
- 💡 **[Suggest new plugin idea](https://github.com/ATreemanDork/treeman-stash-plugins/issues/new?template=plugin-request.md)** *(Coming Soon)*
- 🚀 **[Join the discussion](https://discord.gg/2TsNFKt)** on Stash Discord

### Recognition

Contributors will be:
- 🏆 Listed in plugin documentation
- 🎖️ Credited in release notes  
- 🌟 Featured in repository contributors
- 📢 Mentioned in community announcements

## 🐛 Troubleshooting

### Common Issues

#### Plugin Installation Problems
**Plugin not appearing in Stash**
- ✅ Verify plugin is in correct Stash plugins directory
- ✅ Check file permissions (plugins need read access)
- ✅ Restart Stash after plugin installation
- ✅ Check Stash logs for error messages

**Dependencies not found**
- ✅ Install plugin-specific requirements (`pip install -r requirements.txt`)
- ✅ Verify Python/Node.js version compatibility
- ✅ Check system PATH variables

#### Plugin-Specific Issues

**PerformerSiteSync**
- API connection failures → Verify API keys and endpoints
- Rate limiting errors → Increase rate limit delays
- Cache issues → Clear cache through plugin tasks
- Performance problems → Adjust cache expiration settings

**Future plugins will have specific troubleshooting sections here**

#### Validation Issues
**Schema validation failures**
- Check YAML syntax and indentation
- Ensure required fields are present
- Verify data types match schema requirements

**File validation errors**
- Confirm all referenced files exist
- Check file paths and naming conventions
- Verify permissions on plugin directories

### Getting Help

#### Community Support
- 💬 **[Stash Discord Community](https://discord.gg/2TsNFKt)** - Real-time help and discussion
- 🐛 **[GitHub Issues](https://github.com/ATreemanDork/treeman-stash-plugins/issues)** - Bug reports and feature requests
- 📚 **[Stash Community Scripts](https://github.com/stashapp/CommunityScripts)** - Browse other community plugins

#### Before Asking for Help
1. **Check plugin README** for specific setup instructions
2. **Run validation tools** to identify configuration issues
3. **Review Stash logs** for error messages
4. **Search existing issues** for similar problems
5. **Test with minimal configuration** to isolate problems

#### Reporting Issues
When reporting problems, please include:
- 🖥️ **Operating System** and version
- 🐍 **Python/Node.js version** (if applicable)
- 📋 **Stash version**
- 🔧 **Plugin version** and configuration
- 📝 **Error messages** and log excerpts
- 🔄 **Steps to reproduce** the issue

## 🤖 Developer Resources & AI Assistant References

### Quick Technical Overview
- **Repository Type**: Multi-plugin Stash ecosystem with validation tools
- **Primary Language**: Python (plugins) + Node.js (validation) + PowerShell (automation)
- **Plugin Standard**: [Stash Plugin Schema](validator/plugin.schema.json)
- **Architecture**: Modular plugin system with shared validation infrastructure

### Key Technical Files
| File | Purpose | AI Context |
|------|---------|------------|
| [`validator/plugin.schema.json`](validator/plugin.schema.json) | Official Stash plugin JSON schema | Schema validation reference |
| [`validator/index.js`](validator/index.js) | Node.js validation engine | AJV schema validation patterns |
| [`validate_all.ps1`](validate_all.ps1) | PowerShell multi-platform validator | Cross-platform validation logic |
| [`PerformerSiteSync/performer_site_sync.yml`](PerformerSiteSync/performer_site_sync.yml) | Reference plugin manifest | Plugin structure example |
| [`_template/`](_template/) | Plugin boilerplate templates | New plugin creation patterns |
| [`references/`](references/) | API schemas and introspection data | External API reference documentation |

### Plugin Development Patterns
```yaml
# Standard Plugin Manifest Structure (performer_site_sync.yml)
name: PluginName
description: Plugin description
version: 1.0.0
exec:
  - python
  - "{PluginDir}/plugin_script.py"
interface: raw
tasks:
  - name: "Task Name"
    description: "Task description"
    defaultArgs:
      mode: "task_mode"
```

### Validation Architecture
- **Multi-layer validation**: JSON Schema → File system → Configuration → API connectivity
- **Cross-platform support**: Windows batch, Linux/macOS shell, PowerShell universal
- **CI/CD integration**: GitHub Actions with exit codes for automated testing
- **Error reporting**: Detailed validation feedback with fix suggestions

### External API Integration Patterns
```python
# Standard external API configuration pattern
EXTERNAL_ENDPOINTS = {
    "stashdb": "https://stashdb.org/graphql",
    "tpdb": "https://theporndb.net/graphql", 
    "fansdb": "https://fansdb.cc/graphql"
}
```

### API Schema References
The `references/schema - introspection_results/` directory contains GraphQL schema introspection data for external APIs:
- **`stashdb_schema.json`**: StashDB GraphQL schema definition
- **`stashlocal_schema.json`**: Local Stash instance schema reference  
- **`tpdb_schema.json`**: ThePornDB GraphQL schema definition
- **`tpdb_api.json`**: ThePornDB API endpoint documentation
- **`fanscc_schema.json`**: FansDB schema definition

*These schemas are invaluable for understanding available fields, types, and mutations when developing API integrations.*

### Code Quality Standards
- **Schema compliance**: All plugins must validate against `plugin.schema.json`
- **Documentation**: README.md + inline documentation required
- **Error handling**: Comprehensive try/catch with logging
- **Dependencies**: Explicit version management (requirements.txt/package.json)
- **Testing**: Validation tools + manual Stash instance testing

### Repository Structure Context
```
treeman-stash-plugins/
├── README.md                    # This file - main documentation
├── validator/                   # Node.js schema validation system
├── _template/                   # Plugin creation templates  
├── PerformerSiteSync/          # Reference implementation plugin
├── references/                  # API schemas and technical references
│   └── schema - introspection_results/  # External API schema definitions
├── validate.* scripts          # Cross-platform validation tools
├── new-plugin.ps1              # Automated plugin generator
└── .github/workflows/          # CI/CD automation
```

### AI Assistant Quick Start
1. **Understanding codebase**: Read this README + `PerformerSiteSync/README.md` for patterns
2. **API schemas**: Reference `references/schema - introspection_results/` for external API structures
3. **Validation**: Always run validation tools after any changes
4. **Plugin creation**: Use `new-plugin.ps1` for boilerplate generation
5. **Schema reference**: Check `validator/plugin.schema.json` for required fields
6. **Testing approach**: Multi-platform validation + manual Stash testing

### Common AI Assistant Tasks
- **New plugin creation**: Use template system + follow PerformerSiteSync patterns
- **Validation fixes**: Run validation tools, interpret error messages, apply fixes
- **Documentation updates**: Maintain README.md consistency across plugins
- **Cross-platform compatibility**: Test validation scripts on Windows/Linux/macOS
- **Schema compliance**: Ensure all YAML manifests match plugin.schema.json

### Reference Links for AI Context
- [Stash Plugin Development](https://docs.stashapp.cc/plugins/plugins) - Official plugin documentation
- [Stash In-App Plugin Manual](https://docs.stashapp.cc/in-app-manual/plugins/) - Plugin manager and installation guide
- [Stash GraphQL API](https://docs.stashapp.cc/graphql) - API reference for plugin integration
- [JSON Schema Specification](https://json-schema.org/) - Schema validation standard
- [AJV Schema Validator](https://ajv.js.org/) - Node.js validation library used
- [Stash Community Scripts](https://github.com/stashapp/CommunityScripts) - Community plugin examples

### Plugin Source Information
- **Source URL**: `https://atreemandork.github.io/index.yml`
- **Distribution**: GitHub Releases with automatic packaging
- **Installation**: Stash Plugin Manager compatible
- **Updates**: Automatic version detection and semantic versioning

## 📄 License

This project is licensed under the AGPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Stash Community](https://github.com/stashapp/stash) for the amazing media organizer
- [StashDB](https://stashdb.org), [ThePornDB](https://theporndb.net), and [FansDB](https://fansdb.cc) for providing data APIs
- All contributors and testers who help improve these plugins

## 📊 Project Stats

![GitHub last commit](https://img.shields.io/github/last-commit/ATreemanDork/treeman-stash-plugins)
![GitHub issues](https://img.shields.io/github/issues/ATreemanDork/treeman-stash-plugins)
![GitHub stars](https://img.shields.io/github/stars/ATreemanDork/treeman-stash-plugins)
![License](https://img.shields.io/github/license/ATreemanDork/treeman-stash-plugins)

---

**Made with ❤️ for the Stash community**