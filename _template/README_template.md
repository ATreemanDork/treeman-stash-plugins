# TemplatePlugin

Brief description of what your plugin does and its main purpose.

## 🚀 Features

- **Main Feature**: Description of primary functionality
- **Secondary Feature**: Description of additional capabilities
- **Integration**: Works with specific Stash features or external services
- **Configuration**: Customizable settings for different use cases

## 📋 Requirements

- **Stash**: v0.20.0 or later
- **Python**: 3.8+ (if Python-based)
- **Node.js**: 14+ (if Node.js-based)
- **External APIs**: List any required external services
- **System Requirements**: Any specific OS or hardware requirements

## 🔧 Installation

1. **Download Plugin**
   ```bash
   # Clone the repository
   git clone https://github.com/ATreemanDork/treeman-stash-plugins.git
   cd treeman-stash-plugins
   ```

2. **Install Dependencies**
   ```bash
   # For Python plugins
   pip install -r TemplatePlugin/requirements.txt
   
   # For Node.js plugins
   cd TemplatePlugin && npm install
   ```

3. **Copy to Stash**
   ```bash
   cp -r TemplatePlugin /path/to/stash/plugins/
   ```

4. **Enable in Stash**
   - Go to **Settings → Plugins**
   - Find "TemplatePlugin" and enable it
   - Configure plugin settings as needed

## ⚙️ Configuration

### Plugin Settings

Access plugin settings through: **Settings → Plugins → TemplatePlugin → Plugin Settings**

| Setting | Description | Default | Required |
|---------|-------------|---------|----------|
| **Enable Feature** | Enable/disable main functionality | `true` | No |
| **API Key** | Your external service API key | `""` | Yes* |
| **Cache Expiration** | Cache duration in hours (1-168) | `24` | No |
| **Debug Logging** | Enable detailed logging | `false` | No |

*\*Required only if using external service integration*

### External Service Setup

If your plugin requires external APIs:

1. **Register Account** at [External Service](https://example.com)
2. **Generate API Key** in your account settings
3. **Configure in Plugin** settings
4. **Test Connection** using the built-in test task

## 🎯 Usage

### Manual Tasks

Access tasks through: **Settings → Plugins → TemplatePlugin → Tasks**

#### Main Task
**Purpose**: Primary function of the plugin  
**Usage**: Click "Main Task" to execute the main functionality  
**Options**: Configure behavior through plugin settings

#### Test Connection
**Purpose**: Verify external service connectivity  
**Usage**: Click "Test Connection" to validate your configuration  
**Result**: Shows connection status and any configuration issues

#### Clear Cache
**Purpose**: Force refresh of cached data  
**Usage**: Click "Clear Cache" when you need fresh data  
**Note**: Next operation will take longer as cache rebuilds

### Automatic Triggers

The plugin automatically responds to:
- **Scene Creation**: Processes new scenes as they're added
- **Scene Updates**: Updates metadata when scenes are modified

Configure automatic behavior through plugin settings.

## 🔧 Customization

### Advanced Configuration

Edit the plugin YAML file for advanced customization:

```yaml
# Example advanced settings
settings:
  customOption:
    displayName: Custom Option
    description: Your custom setting description
    type: STRING
    default: "default_value"
```

### Integration with Other Plugins

This plugin can work alongside:
- **OtherPlugin**: Specific integration details
- **ThirdPlugin**: How they complement each other

## 🐛 Troubleshooting

### Common Issues

**Plugin Not Loading**
- ✅ Check Stash logs for error messages
- ✅ Verify dependencies are installed
- ✅ Ensure Python/Node.js version compatibility

**External Service Connection Failed**
- ✅ Verify API key is correct and active
- ✅ Check network connectivity
- ✅ Use "Test Connection" task for diagnostics

**Performance Issues**
- ✅ Increase cache expiration time
- ✅ Enable debug logging to identify bottlenecks
- ✅ Check system resources during operation

**Data Not Updating**
- ✅ Try "Clear Cache" task to force refresh
- ✅ Check if external service is responding
- ✅ Verify plugin settings are correct

### Debug Mode

Enable debug logging for detailed troubleshooting:

1. **Settings → Plugins → TemplatePlugin → Plugin Settings**
2. **Enable "Debug Logging"**
3. **Check Stash logs** for detailed operation information

### Getting Help

- 💬 **[Stash Discord](https://discord.gg/2TsNFKt)** - Community support
- 🐛 **[GitHub Issues](https://github.com/ATreemanDork/treeman-stash-plugins/issues)** - Bug reports
- 📚 **[Main Repository](https://github.com/ATreemanDork/treeman-stash-plugins)** - Documentation and updates

## 📝 Changelog

### v1.0.0
- Initial release
- Core functionality implementation
- Basic configuration options
- External service integration

## 📄 License

This plugin is part of the Treeman's Stash Plugins collection and is licensed under the AGPL-3.0 License.

## 🙏 Acknowledgments

- [Stash Community](https://github.com/stashapp/stash) for the amazing platform
- [External Service](https://example.com) for providing the API
- Contributors and testers who helped improve this plugin
