"""
Configuration Management Module
Handles loading and managing Stash configuration and plugin settings
"""

import stashapi.log as log
from stashapi.stashapp import StashInterface
from typing import Dict, List, Optional, Any


class ConfigManager:
    """Manages configuration loading and validation for the plugin"""
    
    def __init__(self):
        self.stash = StashInterface()
        self._plugin_config = None
        self._endpoints = None
        self._sources = None
        
    @property
    def plugin_config(self) -> Dict[str, Any]:
        """Get plugin configuration, loading if necessary"""
        if self._plugin_config is None:
            self._plugin_config = self._load_plugin_config()
        return self._plugin_config
    
    @property
    def endpoints(self) -> Dict[str, Dict[str, str]]:
        """Get endpoint configuration, loading if necessary"""
        if self._endpoints is None:
            self._endpoints = self._load_stash_configuration()
        return self._endpoints
    
    @property
    def sources(self) -> Dict[str, Dict[str, Any]]:
        """Get sources configuration, loading if necessary"""
        if self._sources is None:
            self._sources = self._build_sources_config()
        return self._sources

    def _load_plugin_config(self) -> Dict[str, Any]:
        """Load plugin configuration from Stash settings"""
        try:
            config = self.stash.get_configuration()
            plugin_config = config.get("plugins", {})
            performer_sync_config = plugin_config.get("PerformerSiteSync", {})
            
            # Default configuration
            default_config = {
                "cacheExpirationHours": 24,
                "rateLimit": 2,
                "enableStashDB": True,
                "enableTPDB": True,
                "enableFansDB": True,
                "sourcePrecedence": "stashdb,tpdb,fansdb",
                "debugLogging": False,
                "performerImageUpdate": True,
                "enableNameSearch": True,  # New setting for name-based searches
                "autoCreateSites": False   # New setting for site auto-creation
            }
            
            # Merge with user configuration
            config = {**default_config, **performer_sync_config}
            
            if config["debugLogging"]:
                log.info(f"Loaded plugin configuration: {config}")
                
            return config
            
        except Exception as e:
            log.error(f"Failed to load plugin configuration: {e}")
            return {
                "cacheExpirationHours": 24,
                "rateLimit": 2,
                "enableStashDB": True,
                "enableTPDB": True,
                "enableFansDB": True,
                "sourcePrecedence": "stashdb,tpdb,fansdb",
                "debugLogging": False,
                "performerImageUpdate": True,
                "enableNameSearch": True,
                "autoCreateSites": False
            }

    def _load_stash_configuration(self) -> Dict[str, Dict[str, str]]:
        """Load endpoint configuration from Stash's stash_boxes configuration"""
        try:
            config = self.stash.get_configuration()
            stash_boxes = config.get("general", {}).get("stashBoxes", [])
            
            endpoints = {}
            endpoint_mapping = {
                'https://stashdb.org/graphql': 'stashdb',
                'https://theporndb.net/graphql': 'tpdb', 
                'https://fansdb.cc/graphql': 'fansdb'
            }
            
            for box in stash_boxes:
                endpoint_url = box.get('endpoint', '')
                api_key = box.get('apikey', '')
                name = box.get('name', '')
                
                # Map endpoint to our source names
                source_name = None
                for url_pattern, mapped_name in endpoint_mapping.items():
                    if url_pattern in endpoint_url:
                        source_name = mapped_name
                        break
                        
                if source_name and api_key:
                    endpoints[source_name] = {
                        'url': endpoint_url,
                        'api_key': api_key,
                        'name': name
                    }
                    log.info(f"Loaded configuration for {source_name}: {name}")
            
            return endpoints
            
        except Exception as e:
            log.error(f"Failed to load Stash configuration: {e}")
            return {}

    def _build_sources_config(self) -> Dict[str, Dict[str, Any]]:
        """Build sources configuration with precedence based on plugin settings"""
        sources = {}
        precedence_order = [s.strip() for s in self.plugin_config["sourcePrecedence"].split(",")]
        
        for i, source in enumerate(precedence_order, 1):
            if source in self.endpoints:
                # Check if source is enabled in plugin config
                enable_key = f"enable{source.upper()}" if source != 'tpdb' else 'enableTPDB'
                if self.plugin_config.get(enable_key, True):
                    sources[source] = {
                        'precedence': i,
                        **self.endpoints[source]
                    }
        
        if not sources:
            log.error("No valid stash box endpoints found in configuration!")
            return {}
            
        log.info(f"Configured sources: {list(sources.keys())}")
        return sources

    def get_enabled_sources(self) -> List[str]:
        """Get list of enabled source names"""
        return list(self.sources.keys())
    
    def is_source_enabled(self, source: str) -> bool:
        """Check if a specific source is enabled"""
        return source in self.sources
    
    def get_source_config(self, source: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific source"""
        return self.sources.get(source)
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate configuration and return validation results"""
        validation_result = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "sources_configured": len(self.endpoints),
            "sources_enabled": len(self.sources),
            "plugin_config": self.plugin_config
        }
        
        # Check if any sources are configured
        if not self.sources:
            validation_result["valid"] = False
            validation_result["issues"].append("No external sources configured in Stash settings")
            
        # Check API keys
        for source, config in self.sources.items():
            if not config.get('api_key'):
                validation_result["valid"] = False
                validation_result["issues"].append(f"No API key configured for {source}")
                
        # Check plugin configuration
        if self.plugin_config["cacheExpirationHours"] < 1 or self.plugin_config["cacheExpirationHours"] > 168:
            validation_result["warnings"].append("Cache expiration should be between 1-168 hours")
            
        if self.plugin_config["rateLimit"] < 0 or self.plugin_config["rateLimit"] > 10:
            validation_result["warnings"].append("Rate limit should be between 0-10 seconds")
            
        return validation_result
    
    def reload_configuration(self):
        """Force reload of all configuration"""
        self._plugin_config = None
        self._endpoints = None
        self._sources = None
        log.info("Configuration reloaded")
