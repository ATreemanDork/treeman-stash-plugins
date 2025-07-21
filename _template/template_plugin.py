#!/usr/bin/env python3
"""
TemplatePlugin for Stash

A template plugin that demonstrates the basic structure and functionality
for creating new Stash plugins.

Author: ATreemanDork
License: AGPL-3.0
"""

import json
import sys
import logging
from typing import Dict, Any, List


class TemplatePlugin:
    """
    Template plugin class that demonstrates basic plugin structure.
    """
    
    def __init__(self):
        """Initialize the template plugin."""
        self.logger = self._setup_logging()
        self.fragment_server = {
            "Scheme": "http",
            "Host": "0.0.0.0",
            "Port": "9999",
            "Path": ""
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the plugin."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def main(self):
        """Main entry point for the plugin."""
        try:
            # Read JSON input from Stash
            json_input = json.loads(sys.stdin.read())
            
            # Get the operation mode
            mode = json_input.get("args", {}).get("mode", "")
            
            if mode == "example_task":
                return self.example_task(json_input)
            elif mode == "health_check":
                return self.health_check()
            else:
                return self.default_operation(json_input)
                
        except Exception as e:
            self.logger.error(f"Plugin execution failed: {str(e)}")
            return {"error": str(e)}
    
    def example_task(self, json_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Example task that demonstrates plugin functionality.
        
        Args:
            json_input: Input data from Stash
            
        Returns:
            Result dictionary
        """
        self.logger.info("Running example task")
        
        # Example: Process some data
        settings = json_input.get("args", {})
        enable_feature = settings.get("enableFeature", True)
        api_key = settings.get("apiKey", "")
        
        if not enable_feature:
            return {"message": "Feature is disabled"}
        
        if not api_key:
            return {"warning": "No API key provided"}
        
        # Simulate some work
        result = {
            "message": "Template plugin executed successfully",
            "feature_enabled": enable_feature,
            "api_configured": bool(api_key),
            "processed_items": 0
        }
        
        self.logger.info("Example task completed")
        return result
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the plugin.
        
        Returns:
            Health status dictionary
        """
        self.logger.info("Performing health check")
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "plugin_name": "TemplatePlugin",
            "dependencies_ok": True
        }
    
    def default_operation(self, json_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Default operation when no specific mode is provided.
        
        Args:
            json_input: Input data from Stash
            
        Returns:
            Default response
        """
        self.logger.info("Running default operation")
        
        return {
            "message": "Template plugin is running",
            "available_modes": ["example_task", "health_check"],
            "input_received": bool(json_input)
        }


if __name__ == "__main__":
    plugin = TemplatePlugin()
    result = plugin.main()
    print(json.dumps(result, indent=2))
