#!/usr/bin/env python3
"""
Standalone validation script for Stash plugins.

This script can validate individual plugin configurations or entire directories
of plugins to ensure they meet Stash plugin standards.
"""

import sys
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

class StashPluginValidator:
    """Validates Stash plugin configurations against schema requirements."""
    
    def __init__(self, verbose: bool = False, allow_warnings: bool = True):
        """Initialize the validator."""
        self.verbose = verbose
        self.allow_warnings = allow_warnings
        self.errors = []
        self.warnings = []
        
    def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate a single plugin YAML file."""
        if self.verbose:
            print(f"Validating: {file_path}")
        
        result = {
            'file': str(file_path),
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Load YAML content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if not isinstance(content, dict):
                result['errors'].append("Plugin configuration must be a YAML object")
                result['valid'] = False
                return result
            
            # Validate required fields
            self._validate_required_fields(content, result)
            
            # Validate field types and formats
            self._validate_field_types(content, result)
            
            # Validate plugin structure
            self._validate_plugin_structure(content, result)
            
            # Validate tasks
            if 'tasks' in content:
                self._validate_tasks(content['tasks'], result)
            
            # Validate settings
            if 'settings' in content:
                self._validate_settings(content['settings'], result)
            
            # Validate hooks
            if 'hooks' in content:
                self._validate_hooks(content['hooks'], result)
            
            # Validate UI configuration
            if 'ui' in content:
                self._validate_ui_config(content['ui'], result, file_path.parent)
                
        except yaml.YAMLError as e:
            result['errors'].append(f"YAML parsing error: {str(e)}")
            result['valid'] = False
        except Exception as e:
            result['errors'].append(f"Validation error: {str(e)}")
            result['valid'] = False
        
        # Set overall validity
        result['valid'] = len(result['errors']) == 0
        
        return result
    
    def _validate_required_fields(self, content: Dict[str, Any], result: Dict[str, Any]):
        """Validate required fields are present."""
        required_fields = ['name']
        
        for field in required_fields:
            if field not in content:
                result['errors'].append(f"Missing required field: '{field}'")
    
    def _validate_field_types(self, content: Dict[str, Any], result: Dict[str, Any]):
        """Validate field types and formats."""
        
        # String fields
        string_fields = ['name', 'description', 'url', 'interface', 'errLog']
        for field in string_fields:
            if field in content and not isinstance(content[field], str):
                result['errors'].append(f"Field '{field}' must be a string")
        
        # Version validation
        if 'version' in content:
            version = str(content['version'])
            if not self._is_valid_version(version):
                result['errors'].append(f"Invalid version format: '{version}' (should be x.y.z)")
        
        # Interface validation
        if 'interface' in content:
            valid_interfaces = ['raw', 'rpc', 'js']
            if content['interface'] not in valid_interfaces:
                result['errors'].append(f"Invalid interface: '{content['interface']}' (must be one of: {', '.join(valid_interfaces)})")
        
        # Error log level validation
        if 'errLog' in content:
            valid_levels = ['trace', 'debug', 'info', 'warning', 'error']
            if content['errLog'] not in valid_levels:
                result['errors'].append(f"Invalid errLog level: '{content['errLog']}' (must be one of: {', '.join(valid_levels)})")
        
        # Exec validation
        if 'exec' in content:
            if not isinstance(content['exec'], list):
                result['errors'].append("Field 'exec' must be an array")
            elif len(content['exec']) == 0:
                result['errors'].append("Field 'exec' cannot be empty")
            else:
                for i, item in enumerate(content['exec']):
                    if not isinstance(item, str):
                        result['errors'].append(f"exec[{i}] must be a string")
    
    def _validate_plugin_structure(self, content: Dict[str, Any], result: Dict[str, Any]):
        """Validate overall plugin structure."""
        
        # Check for at least one of tasks or hooks
        if 'tasks' not in content and 'hooks' not in content:
            result['warnings'].append("Plugin should define either 'tasks' or 'hooks' (or both)")
        
        # Validate that exec is present if interface is not js
        interface = content.get('interface', 'raw')
        if interface != 'js' and 'exec' not in content:
            result['errors'].append("Field 'exec' is required when interface is not 'js'")
        
        # JavaScript plugins should not have exec
        if interface == 'js' and 'exec' in content:
            result['warnings'].append("JavaScript plugins (interface: js) should not define 'exec'")
    
    def _validate_tasks(self, tasks: Any, result: Dict[str, Any]):
        """Validate tasks configuration."""
        
        if not isinstance(tasks, list):
            result['errors'].append("Field 'tasks' must be an array")
            return
        
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                result['errors'].append(f"tasks[{i}] must be an object")
                continue
            
            # Required task fields
            if 'name' not in task:
                result['errors'].append(f"tasks[{i}] missing required field 'name'")
            
            # Recommended task fields
            if 'description' not in task:
                result['warnings'].append(f"tasks[{i}] should have a 'description' field")
            
            # Validate task fields
            if 'name' in task and not isinstance(task['name'], str):
                result['errors'].append(f"tasks[{i}].name must be a string")
            
            if 'description' in task and not isinstance(task['description'], str):
                result['errors'].append(f"tasks[{i}].description must be a string")
            
            if 'defaultArgs' in task and not isinstance(task['defaultArgs'], dict):
                result['errors'].append(f"tasks[{i}].defaultArgs must be an object")
    
    def _validate_settings(self, settings: Any, result: Dict[str, Any]):
        """Validate settings configuration."""
        
        if not isinstance(settings, dict):
            result['errors'].append("Field 'settings' must be an object")
            return
        
        for setting_name, setting_config in settings.items():
            if not isinstance(setting_config, dict):
                result['errors'].append(f"settings.{setting_name} must be an object")
                continue
            
            # Required setting fields
            if 'type' not in setting_config:
                result['errors'].append(f"settings.{setting_name} missing required field 'type'")
            else:
                valid_types = ['STRING', 'NUMBER', 'BOOLEAN']
                if setting_config['type'] not in valid_types:
                    result['errors'].append(f"settings.{setting_name}.type must be one of: {', '.join(valid_types)}")
            
            # Recommended setting fields
            if 'displayName' not in setting_config:
                result['warnings'].append(f"settings.{setting_name} should have a 'displayName' field")
            
            if 'description' not in setting_config:
                result['warnings'].append(f"settings.{setting_name} should have a 'description' field")
            
            # Validate setting field types
            string_fields = ['displayName', 'description']
            for field in string_fields:
                if field in setting_config and not isinstance(setting_config[field], str):
                    result['errors'].append(f"settings.{setting_name}.{field} must be a string")
    
    def _validate_hooks(self, hooks: Any, result: Dict[str, Any]):
        """Validate hooks configuration."""
        
        if not isinstance(hooks, list):
            result['errors'].append("Field 'hooks' must be an array")
            return
        
        valid_triggers = [
            'Scene.Create.Post', 'Scene.Update.Post', 'Scene.Destroy.Post',
            'Image.Create.Post', 'Image.Update.Post', 'Image.Destroy.Post',
            'Gallery.Create.Post', 'Gallery.Update.Post', 'Gallery.Destroy.Post',
            'Movie.Create.Post', 'Movie.Update.Post', 'Movie.Destroy.Post',
            'Performer.Create.Post', 'Performer.Update.Post', 'Performer.Destroy.Post',
            'Studio.Create.Post', 'Studio.Update.Post', 'Studio.Destroy.Post',
            'Tag.Create.Post', 'Tag.Update.Post', 'Tag.Destroy.Post'
        ]
        
        for i, hook in enumerate(hooks):
            if not isinstance(hook, dict):
                result['errors'].append(f"hooks[{i}] must be an object")
                continue
            
            # Required hook fields
            if 'triggeredBy' not in hook:
                result['errors'].append(f"hooks[{i}] missing required field 'triggeredBy'")
            else:
                if not isinstance(hook['triggeredBy'], list):
                    result['errors'].append(f"hooks[{i}].triggeredBy must be an array")
                else:
                    for j, trigger in enumerate(hook['triggeredBy']):
                        if trigger not in valid_triggers:
                            result['warnings'].append(f"hooks[{i}].triggeredBy[{j}] unknown trigger: '{trigger}'")
    
    def _validate_ui_config(self, ui: Any, result: Dict[str, Any], plugin_dir: Path):
        """Validate UI configuration."""
        
        if not isinstance(ui, dict):
            result['errors'].append("Field 'ui' must be an object")
            return
        
        # Must have at least one of css or javascript
        if 'css' not in ui and 'javascript' not in ui:
            result['errors'].append("ui configuration must define either 'css' or 'javascript' (or both)")
        
        # Validate CSS files
        if 'css' in ui:
            if isinstance(ui['css'], str):
                css_files = [ui['css']]
            elif isinstance(ui['css'], list):
                css_files = ui['css']
            else:
                result['errors'].append("ui.css must be a string or array of strings")
                css_files = []
            
            for css_file in css_files:
                if not isinstance(css_file, str):
                    result['errors'].append("ui.css files must be strings")
                    continue
                
                file_path = plugin_dir / css_file
                if not file_path.exists():
                    result['warnings'].append(f"CSS file not found: {css_file}")
        
        # Validate JavaScript files
        if 'javascript' in ui:
            if isinstance(ui['javascript'], str):
                js_files = [ui['javascript']]
            elif isinstance(ui['javascript'], list):
                js_files = ui['javascript']
            else:
                result['errors'].append("ui.javascript must be a string or array of strings")
                js_files = []
            
            for js_file in js_files:
                if not isinstance(js_file, str):
                    result['errors'].append("ui.javascript files must be strings")
                    continue
                
                file_path = plugin_dir / js_file
                if not file_path.exists():
                    result['warnings'].append(f"JavaScript file not found: {js_file}")
    
    def _is_valid_version(self, version: str) -> bool:
        """Check if version string follows semantic versioning."""
        pattern = r'^\d+(\.\d+)?(\.\d+)?$'
        return bool(re.match(pattern, version))
    
    def validate_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """Validate all plugin files in a directory."""
        results = []
        
        # Find all YAML files
        yaml_files = list(directory.glob("*.yml")) + list(directory.glob("*.yaml"))
        
        # Exclude files that are not plugin configurations
        excluded_files = {
            'index.yml',           # Plugin source index
            '_config.yml',         # GitHub Pages config
            '.github/workflows',   # CI/CD workflows
            'docker-compose.yml',  # Docker config
            'mkdocs.yml',         # Documentation config
        }
        
        plugin_files = []
        for yaml_file in yaml_files:
            # Skip if file name is in excluded list
            if yaml_file.name in excluded_files:
                if self.verbose:
                    print(f"Skipping non-plugin file: {yaml_file.name}")
                continue
            
            # Skip if file is in excluded directories
            if any(part.startswith('.') for part in yaml_file.parts):
                if self.verbose:
                    print(f"Skipping hidden directory file: {yaml_file}")
                continue
            
            plugin_files.append(yaml_file)
        
        if not plugin_files:
            if self.verbose:
                print(f"No plugin YAML files found in {directory}")
            return results
        
        for yaml_file in plugin_files:
            if self.verbose:
                print(f"Validating: {yaml_file.name}")
            result = self.validate_file(yaml_file)
            results.append(result)
        
        return results
    
    def print_results(self, results: List[Dict[str, Any]]):
        """Print validation results in a readable format."""
        
        total_files = len(results)
        valid_files = sum(1 for r in results if r['valid'])
        
        print(f"\n{'='*60}")
        print(f"STASH PLUGIN VALIDATION RESULTS")
        print(f"{'='*60}")
        print(f"Total files: {total_files}")
        print(f"Valid files: {valid_files}")
        print(f"Invalid files: {total_files - valid_files}")
        print(f"{'='*60}")
        
        for result in results:
            file_name = Path(result['file']).name
            status = "[PASS]" if result['valid'] else "[FAIL]"
            print(f"\n{status} {file_name}")
            
            if result['errors']:
                print("  Errors:")
                for error in result['errors']:
                    print(f"    [ERROR] {error}")
            
            if result['warnings'] and (self.verbose or not result['valid']):
                print("  Warnings:")
                for warning in result['warnings']:
                    print(f"    [WARNING] {warning}")
        
        print(f"\n{'='*60}")
        
        if valid_files == total_files:
            print("[SUCCESS] All plugin configurations are valid!")
        else:
            print("[ERROR] Some plugin configurations have issues. Please review and fix.")

def main():
    """Main entry point for the validation script."""
    
    parser = argparse.ArgumentParser(
        description="Validate Stash plugin configurations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_plugins.py plugin.yml
  python validate_plugins.py --directory /path/to/plugins
  python validate_plugins.py --verbose plugin.yml
  python validate_plugins.py --ci /path/to/plugins
        """
    )
    
    parser.add_argument(
        'path', 
        nargs='?',
        help='Path to plugin file or directory to validate'
    )
    
    parser.add_argument(
        '--directory', '-d',
        help='Validate all plugins in the specified directory'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--ci',
        action='store_true',
        help='CI mode: exit with error code if validation fails'
    )
    
    parser.add_argument(
        '--no-warnings',
        action='store_true',
        help='Treat warnings as errors'
    )
    
    args = parser.parse_args()
    
    # Determine what to validate
    if args.directory:
        target_path = Path(args.directory)
        if not target_path.is_dir():
            print(f"Error: {args.directory} is not a directory")
            sys.exit(1)
        is_directory = True
    elif args.path:
        target_path = Path(args.path)
        if not target_path.exists():
            print(f"Error: {args.path} does not exist")
            sys.exit(1)
        is_directory = target_path.is_dir()
    else:
        # Default to current directory
        target_path = Path.cwd()
        is_directory = True
    
    # Initialize validator
    validator = StashPluginValidator(
        verbose=args.verbose,
        allow_warnings=not args.no_warnings
    )
    
    # Run validation
    if is_directory:
        results = validator.validate_directory(target_path)
    else:
        results = [validator.validate_file(target_path)]
    
    # Print results
    validator.print_results(results)
    
    # Exit with appropriate code for CI
    if args.ci:
        all_valid = all(r['valid'] for r in results)
        if not args.no_warnings:
            # In CI mode with warnings allowed, only fail on errors
            sys.exit(0 if all_valid else 1)
        else:
            # In CI mode with no warnings, fail on errors or warnings
            has_warnings = any(r['warnings'] for r in results)
            sys.exit(0 if all_valid and not has_warnings else 1)

if __name__ == "__main__":
    main()
