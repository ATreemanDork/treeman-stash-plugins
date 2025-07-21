"""
Plugin configuration validation module for PerformerSiteSync.

This module provides validation capabilities for the plugin configuration,
external API endpoints, and runtime settings to ensure proper operation.
"""

import yaml
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from .config import ConfigManager

logger = logging.getLogger(__name__)

class ConfigValidator:
    """Validates plugin configuration and external API connectivity."""
    
    def __init__(self, config: ConfigManager):
        """Initialize validator with plugin configuration."""
        self.config = config
        self.validation_results = {}
        
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks and return comprehensive results."""
        logger.info("Starting comprehensive configuration validation")
        
        results = {
            'overall_status': True,
            'timestamp': self.config.get_current_timestamp(),
            'plugin_config': self._validate_plugin_config(),
            'external_apis': self._validate_external_apis(),
            'settings': self._validate_settings(),
            'dependencies': self._validate_dependencies(),
            'file_permissions': self._validate_file_permissions()
        }
        
        # Determine overall status
        results['overall_status'] = all([
            results['plugin_config']['valid'],
            results['external_apis']['valid'],
            results['settings']['valid'],
            results['dependencies']['valid'],
            results['file_permissions']['valid']
        ])
        
        logger.info(f"Validation completed. Overall status: {'PASS' if results['overall_status'] else 'FAIL'}")
        return results
    
    def _validate_plugin_config(self) -> Dict[str, Any]:
        """Validate the plugin YAML configuration against schema."""
        logger.debug("Validating plugin configuration file")
        
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'config_file': None
        }
        
        try:
            # Find the plugin YAML file
            plugin_dir = Path(__file__).parent.parent
            yaml_files = list(plugin_dir.glob("*.yml")) + list(plugin_dir.glob("*.yaml"))
            
            if not yaml_files:
                result['errors'].append("No plugin YAML configuration file found")
                result['valid'] = False
                return result
                
            config_file = yaml_files[0]  # Use the first YAML file found
            result['config_file'] = str(config_file)
            
            # Load and parse YAML
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # Validate required fields
            required_fields = ['name', 'description', 'version', 'exec', 'interface', 'tasks']
            for field in required_fields:
                if field not in config_data:
                    result['errors'].append(f"Missing required field: {field}")
                    result['valid'] = False
            
            # Validate version format
            if 'version' in config_data:
                version = str(config_data['version'])
                if not self._is_valid_version(version):
                    result['errors'].append(f"Invalid version format: {version}")
                    result['valid'] = False
            
            # Validate interface
            if 'interface' in config_data:
                valid_interfaces = ['raw', 'rpc', 'js']
                if config_data['interface'] not in valid_interfaces:
                    result['errors'].append(f"Invalid interface: {config_data['interface']}")
                    result['valid'] = False
            
            # Validate tasks structure
            if 'tasks' in config_data:
                if not isinstance(config_data['tasks'], list):
                    result['errors'].append("Tasks must be a list")
                    result['valid'] = False
                else:
                    for i, task in enumerate(config_data['tasks']):
                        if not isinstance(task, dict):
                            result['errors'].append(f"Task {i} must be an object")
                            result['valid'] = False
                            continue
                        
                        if 'name' not in task:
                            result['errors'].append(f"Task {i} missing required 'name' field")
                            result['valid'] = False
                        
                        if 'description' not in task:
                            result['warnings'].append(f"Task {i} missing recommended 'description' field")
            
            # Validate settings structure
            if 'settings' in config_data:
                settings = config_data['settings']
                if not isinstance(settings, dict):
                    result['errors'].append("Settings must be an object")
                    result['valid'] = False
                else:
                    for setting_name, setting_config in settings.items():
                        if not isinstance(setting_config, dict):
                            result['errors'].append(f"Setting '{setting_name}' must be an object")
                            result['valid'] = False
                            continue
                        
                        if 'type' not in setting_config:
                            result['errors'].append(f"Setting '{setting_name}' missing required 'type' field")
                            result['valid'] = False
                        
                        valid_types = ['STRING', 'NUMBER', 'BOOLEAN']
                        if setting_config.get('type') not in valid_types:
                            result['errors'].append(f"Setting '{setting_name}' has invalid type: {setting_config.get('type')}")
                            result['valid'] = False
            
        except Exception as e:
            result['errors'].append(f"Error parsing configuration file: {str(e)}")
            result['valid'] = False
        
        return result
    
    def _validate_external_apis(self) -> Dict[str, Any]:
        """Validate connectivity to external API endpoints."""
        logger.debug("Validating external API connectivity")
        
        result = {
            'valid': True,
            'endpoints': {},
            'errors': [],
            'warnings': []
        }
        
        endpoints = self.config.get_stashbox_endpoints()
        
        if not endpoints:
            result['warnings'].append("No external API endpoints configured")
            return result
        
        for endpoint in endpoints:
            endpoint_name = endpoint.get('name', 'Unknown')
            endpoint_url = endpoint.get('endpoint', '')
            api_key = endpoint.get('api_key', '')
            
            endpoint_result = {
                'name': endpoint_name,
                'url': endpoint_url,
                'has_api_key': bool(api_key),
                'connectivity': 'unknown',
                'response_time': None,
                'error': None
            }
            
            if not endpoint_url:
                endpoint_result['error'] = "Missing endpoint URL"
                endpoint_result['connectivity'] = 'failed'
                result['valid'] = False
                result['errors'].append(f"Endpoint '{endpoint_name}' missing URL")
            elif not api_key:
                endpoint_result['error'] = "Missing API key"
                endpoint_result['connectivity'] = 'failed'
                result['valid'] = False
                result['errors'].append(f"Endpoint '{endpoint_name}' missing API key")
            else:
                # Test connectivity
                try:
                    import time
                    start_time = time.time()
                    
                    headers = {
                        'ApiKey': api_key,
                        'Content-Type': 'application/json',
                        'User-Agent': 'PerformerSiteSync/1.0.0'
                    }
                    
                    # Simple introspection query to test connectivity
                    test_query = {
                        'query': '''
                        query {
                            __schema {
                                queryType {
                                    name
                                }
                            }
                        }
                        '''
                    }
                    
                    response = requests.post(
                        endpoint_url,
                        json=test_query,
                        headers=headers,
                        timeout=10
                    )
                    
                    endpoint_result['response_time'] = round(time.time() - start_time, 3)
                    
                    if response.status_code == 200:
                        endpoint_result['connectivity'] = 'success'
                    elif response.status_code == 401:
                        endpoint_result['connectivity'] = 'auth_failed'
                        endpoint_result['error'] = "Authentication failed - check API key"
                        result['errors'].append(f"Authentication failed for '{endpoint_name}'")
                        result['valid'] = False
                    else:
                        endpoint_result['connectivity'] = 'failed'
                        endpoint_result['error'] = f"HTTP {response.status_code}"
                        result['errors'].append(f"HTTP error {response.status_code} for '{endpoint_name}'")
                        result['valid'] = False
                        
                except requests.exceptions.Timeout:
                    endpoint_result['connectivity'] = 'timeout'
                    endpoint_result['error'] = "Connection timeout"
                    result['errors'].append(f"Connection timeout for '{endpoint_name}'")
                    result['valid'] = False
                    
                except requests.exceptions.ConnectionError:
                    endpoint_result['connectivity'] = 'connection_error'
                    endpoint_result['error'] = "Connection failed"
                    result['errors'].append(f"Connection failed for '{endpoint_name}'")
                    result['valid'] = False
                    
                except Exception as e:
                    endpoint_result['connectivity'] = 'error'
                    endpoint_result['error'] = str(e)
                    result['errors'].append(f"Error testing '{endpoint_name}': {str(e)}")
                    result['valid'] = False
            
            result['endpoints'][endpoint_name] = endpoint_result
        
        return result
    
    def _validate_settings(self) -> Dict[str, Any]:
        """Validate plugin settings values."""
        logger.debug("Validating plugin settings")
        
        result = {
            'valid': True,
            'settings': {},
            'errors': [],
            'warnings': []
        }
        
        # Validate cache expiration
        cache_hours = self.config.get_setting('cacheExpirationHours', 24)
        if not isinstance(cache_hours, (int, float)) or cache_hours < 1 or cache_hours > 168:
            result['errors'].append(f"Invalid cache expiration: {cache_hours} (must be 1-168 hours)")
            result['valid'] = False
        result['settings']['cacheExpirationHours'] = cache_hours
        
        # Validate rate limit
        rate_limit = self.config.get_setting('rateLimit', 2)
        if not isinstance(rate_limit, (int, float)) or rate_limit < 0 or rate_limit > 10:
            result['errors'].append(f"Invalid rate limit: {rate_limit} (must be 0-10 seconds)")
            result['valid'] = False
        result['settings']['rateLimit'] = rate_limit
        
        # Validate source precedence
        precedence = self.config.get_setting('sourcePrecedence', 'stashdb,tpdb,fansdb')
        if isinstance(precedence, str):
            sources = [s.strip().lower() for s in precedence.split(',')]
            valid_sources = ['stashdb', 'tpdb', 'fansdb']
            invalid_sources = [s for s in sources if s not in valid_sources]
            if invalid_sources:
                result['errors'].append(f"Invalid sources in precedence: {invalid_sources}")
                result['valid'] = False
        else:
            result['errors'].append("Source precedence must be a comma-separated string")
            result['valid'] = False
        result['settings']['sourcePrecedence'] = precedence
        
        # Validate boolean settings
        boolean_settings = [
            'enableStashDB', 'enableTPDB', 'enableFansDB',
            'debugLogging', 'enableNameSearch', 'autoCreateSites',
            'autoCreatePerformers', 'performerImageUpdate'
        ]
        
        for setting in boolean_settings:
            value = self.config.get_setting(setting, False)
            if not isinstance(value, bool):
                result['warnings'].append(f"Setting '{setting}' should be boolean, got {type(value).__name__}")
            result['settings'][setting] = value
        
        return result
    
    def _validate_dependencies(self) -> Dict[str, Any]:
        """Validate Python dependencies are available."""
        logger.debug("Validating Python dependencies")
        
        result = {
            'valid': True,
            'dependencies': {},
            'errors': [],
            'warnings': []
        }
        
        required_modules = [
            'requests', 'pathlib', 'sqlite3', 'json', 'yaml'
        ]
        
        optional_modules = [
            'stashapi'
        ]
        
        for module_name in required_modules:
            try:
                __import__(module_name)
                result['dependencies'][module_name] = {'available': True, 'required': True}
            except ImportError:
                result['dependencies'][module_name] = {'available': False, 'required': True}
                result['errors'].append(f"Required module '{module_name}' not available")
                result['valid'] = False
        
        for module_name in optional_modules:
            try:
                __import__(module_name)
                result['dependencies'][module_name] = {'available': True, 'required': False}
            except ImportError:
                result['dependencies'][module_name] = {'available': False, 'required': False}
                result['warnings'].append(f"Optional module '{module_name}' not available")
        
        return result
    
    def _validate_file_permissions(self) -> Dict[str, Any]:
        """Validate file system permissions for cache and logs."""
        logger.debug("Validating file system permissions")
        
        result = {
            'valid': True,
            'paths': {},
            'errors': [],
            'warnings': []
        }
        
        plugin_dir = Path(__file__).parent.parent
        
        # Check plugin directory permissions
        result['paths']['plugin_dir'] = {
            'path': str(plugin_dir),
            'exists': plugin_dir.exists(),
            'readable': plugin_dir.is_dir() and plugin_dir.exists(),
            'writable': False
        }
        
        try:
            # Test write permission by creating a temporary file
            test_file = plugin_dir / '.test_write_permission'
            test_file.touch()
            test_file.unlink()
            result['paths']['plugin_dir']['writable'] = True
        except Exception:
            result['paths']['plugin_dir']['writable'] = False
            result['warnings'].append("Plugin directory is not writable (cache may not work)")
        
        # Check cache directory
        cache_dir = plugin_dir / 'cache'
        result['paths']['cache_dir'] = {
            'path': str(cache_dir),
            'exists': cache_dir.exists(),
            'readable': cache_dir.exists() and cache_dir.is_dir(),
            'writable': False
        }
        
        if cache_dir.exists():
            try:
                test_file = cache_dir / '.test_write_permission'
                test_file.touch()
                test_file.unlink()
                result['paths']['cache_dir']['writable'] = True
            except Exception:
                result['errors'].append("Cache directory is not writable")
                result['valid'] = False
        else:
            try:
                cache_dir.mkdir(exist_ok=True)
                result['paths']['cache_dir']['exists'] = True
                result['paths']['cache_dir']['readable'] = True
                result['paths']['cache_dir']['writable'] = True
            except Exception:
                result['errors'].append("Cannot create cache directory")
                result['valid'] = False
        
        return result
    
    def _is_valid_version(self, version: str) -> bool:
        """Check if version string follows semantic versioning."""
        import re
        pattern = r'^\d+(\.\d+)?(\.\d+)?$'
        return bool(re.match(pattern, version))
    
    def generate_validation_report(self) -> str:
        """Generate a human-readable validation report."""
        results = self.validate_all()
        
        report_lines = [
            "=" * 60,
            "PERFORMER SITE SYNC - CONFIGURATION VALIDATION REPORT",
            "=" * 60,
            f"Timestamp: {results['timestamp']}",
            f"Overall Status: {'✅ PASS' if results['overall_status'] else '❌ FAIL'}",
            ""
        ]
        
        # Plugin Configuration Section
        plugin_config = results['plugin_config']
        report_lines.extend([
            "📋 PLUGIN CONFIGURATION",
            "-" * 30,
            f"Status: {'✅ Valid' if plugin_config['valid'] else '❌ Invalid'}",
        ])
        
        if plugin_config.get('config_file'):
            report_lines.append(f"Config File: {plugin_config['config_file']}")
        
        if plugin_config['errors']:
            report_lines.append("Errors:")
            for error in plugin_config['errors']:
                report_lines.append(f"  ❌ {error}")
        
        if plugin_config['warnings']:
            report_lines.append("Warnings:")
            for warning in plugin_config['warnings']:
                report_lines.append(f"  ⚠️ {warning}")
        
        report_lines.append("")
        
        # External APIs Section
        external_apis = results['external_apis']
        report_lines.extend([
            "🌐 EXTERNAL API CONNECTIVITY",
            "-" * 30,
            f"Status: {'✅ Valid' if external_apis['valid'] else '❌ Invalid'}",
        ])
        
        for endpoint_name, endpoint_data in external_apis['endpoints'].items():
            status_icon = {
                'success': '✅',
                'failed': '❌',
                'auth_failed': '🔑',
                'timeout': '⏱️',
                'connection_error': '🔌',
                'error': '❌',
                'unknown': '❓'
            }.get(endpoint_data['connectivity'], '❓')
            
            report_lines.append(f"  {status_icon} {endpoint_name}")
            report_lines.append(f"    URL: {endpoint_data['url']}")
            report_lines.append(f"    API Key: {'✅' if endpoint_data['has_api_key'] else '❌'}")
            
            if endpoint_data['response_time']:
                report_lines.append(f"    Response Time: {endpoint_data['response_time']}s")
            
            if endpoint_data['error']:
                report_lines.append(f"    Error: {endpoint_data['error']}")
        
        report_lines.append("")
        
        # Settings Section
        settings = results['settings']
        report_lines.extend([
            "⚙️ PLUGIN SETTINGS",
            "-" * 30,
            f"Status: {'✅ Valid' if settings['valid'] else '❌ Invalid'}",
        ])
        
        for setting_name, setting_value in settings['settings'].items():
            report_lines.append(f"  {setting_name}: {setting_value}")
        
        if settings['errors']:
            report_lines.append("Errors:")
            for error in settings['errors']:
                report_lines.append(f"  ❌ {error}")
        
        if settings['warnings']:
            report_lines.append("Warnings:")
            for warning in settings['warnings']:
                report_lines.append(f"  ⚠️ {warning}")
        
        report_lines.append("")
        
        # Dependencies Section
        dependencies = results['dependencies']
        report_lines.extend([
            "📦 DEPENDENCIES",
            "-" * 30,
            f"Status: {'✅ Valid' if dependencies['valid'] else '❌ Invalid'}",
        ])
        
        for dep_name, dep_info in dependencies['dependencies'].items():
            status_icon = '✅' if dep_info['available'] else ('❌' if dep_info['required'] else '⚠️')
            req_text = 'Required' if dep_info['required'] else 'Optional'
            report_lines.append(f"  {status_icon} {dep_name} ({req_text})")
        
        report_lines.append("")
        
        # File Permissions Section
        file_perms = results['file_permissions']
        report_lines.extend([
            "📁 FILE SYSTEM PERMISSIONS",
            "-" * 30,
            f"Status: {'✅ Valid' if file_perms['valid'] else '❌ Invalid'}",
        ])
        
        for path_name, path_info in file_perms['paths'].items():
            report_lines.append(f"  📁 {path_name}")
            report_lines.append(f"    Path: {path_info['path']}")
            report_lines.append(f"    Exists: {'✅' if path_info['exists'] else '❌'}")
            report_lines.append(f"    Readable: {'✅' if path_info['readable'] else '❌'}")
            report_lines.append(f"    Writable: {'✅' if path_info['writable'] else '❌'}")
        
        report_lines.extend([
            "",
            "=" * 60,
            "End of Report",
            "=" * 60
        ])
        
        return "\n".join(report_lines)
