#!/usr/bin/env python3
"""
Performer/Site Sync Plugin for Stash
Sync performer data between StashDB, ThePornDB, FansDB and local Stash
Based on stashPerformerMatchScrape.py with modular task-based architecture
"""

import stashapi.log as log
import json
import sys
from datetime import datetime
from typing import Dict, Any

# Import modular components
from modules import (
    ConfigManager,
    GraphQLClient,
    PerformerSync,
    FavoritePerformers,
    FavoriteSites
)
from modules.validator import ConfigValidator

class PerformerSiteSyncPlugin:
    """Main plugin class that coordinates all sync operations"""
    
    def __init__(self, server_connection=None):
        """Initialize the plugin with all modular components"""
        try:
            # Initialize configuration manager
            log.info("Initializing ConfigManager...")
            self.config = ConfigManager(server_connection)
            log.info("ConfigManager initialized successfully")
            
            # Initialize GraphQL client
            log.info("Initializing GraphQLClient...")
            self.graphql = GraphQLClient(self.config)
            log.info("GraphQLClient initialized successfully")
            
            # Initialize sync modules
            log.info("Initializing PerformerSync...")
            self.performer_sync = PerformerSync(self.config, self.graphql)
            log.info("PerformerSync initialized successfully")
            
            log.info("Initializing FavoritePerformers...")
            self.favorite_performers = FavoritePerformers(self.config, self.graphql)
            log.info("FavoritePerformers initialized successfully")
            
            log.info("Initializing FavoriteSites...")
            self.favorite_sites = FavoriteSites(self.config, self.graphql)
            log.info("FavoriteSites initialized successfully")
            
            log.info("Performer/Site Sync plugin initialized successfully")
            
        except Exception as e:
            log.error(f"Failed to initialize plugin: {str(e)}")
            import traceback
            log.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_connections(self) -> Dict[str, Any]:
        """Test connectivity to all configured sources"""
        log.info("Testing connections to external sources...")
        
        results = {}
        
        for source in self.config.get_enabled_sources():
            result = self.graphql.test_connection(source)
            results[source] = result
            
            if result["status"] == "connected":
                log.info(f"✓ {result['source']}: Connected ({result['response_time']}ms)")
            else:
                log.error(f"✗ {result['source']}: {result.get('error', 'Failed')}")
        
        return results

    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and report issues"""
        log.info("Running comprehensive configuration validation...")
        
        try:
            # Initialize validator
            validator = ConfigValidator(self.config)
            
            # Run full validation
            validation_results = validator.validate_all()
            
            # Generate human-readable report
            report = validator.generate_validation_report()
            
            # Log the report
            log.info("Validation Report:")
            for line in report.split('\n'):
                log.info(line)
            
            # Return structured results
            return {
                "valid": validation_results['overall_status'],
                "report": report,
                "details": validation_results,
                "timestamp": validation_results['timestamp']
            }
            
        except Exception as e:
            error_msg = f"Failed to validate configuration: {str(e)}"
            log.error(error_msg)
            return {
                "valid": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }

    def clear_cache(self) -> Dict[str, Any]:
        """Clear all cached data"""
        log.info("Clearing all cache data...")
        return self.graphql.clear_cache()

    def generate_sync_report(self) -> Dict[str, Any]:
        """Generate comprehensive sync status report"""
        log.info("Generating sync report...")
        
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "configuration": {
                    "plugin_config": self.config.plugin_config,
                    "enabled_sources": self.config.get_enabled_sources(),
                    "validation": self.config.validate_configuration()
                },
                "connections": self.test_connections(),
                "statistics": {
                    "performers": self.performer_sync.get_performer_statistics(),
                    "favorite_performers": self.favorite_performers.get_favorite_statistics(),
                    "studios": self.favorite_sites.get_studio_statistics()
                }
            }
            
            log.info("Sync report generated successfully")
            return report
            
        except Exception as e:
            error_msg = f"Failed to generate sync report: {str(e)}"
            log.error(error_msg)
            return {"error": error_msg}

    # Task routing methods
    def update_all_performers(self, args: Dict = None) -> Dict[str, Any]:
        """Route to performer sync - update all performers"""
        enable_name_search = args.get("enableNameSearch") if args else None
        return self.performer_sync.update_all_performers(enable_name_search)

    def update_single_performer(self, args: Dict = None) -> Dict[str, Any]:
        """Route to performer sync - update single performer"""
        if not args or "performer_id" not in args:
            return {"error": "performer_id required for single performer update"}
        
        performer_id = args["performer_id"]
        enable_name_search = args.get("enableNameSearch")
        return self.performer_sync.update_single_performer(performer_id, enable_name_search)

    def sync_all_favorites(self, args: Dict = None) -> Dict[str, Any]:
        """Route to favorite performers sync - all sources"""
        return self.favorite_performers.sync_all_favorites()

    def sync_stashdb_favorites(self, args: Dict = None) -> Dict[str, Any]:
        """Route to favorite performers sync - StashDB only"""
        return self.favorite_performers.sync_stashdb_favorites()

    def sync_tpdb_favorites(self, args: Dict = None) -> Dict[str, Any]:
        """Route to favorite performers sync - TPDB only"""
        return self.favorite_performers.sync_tpdb_favorites()

    def sync_fansdb_favorites(self, args: Dict = None) -> Dict[str, Any]:
        """Route to favorite performers sync - FansDB only"""
        return self.favorite_performers.sync_fansdb_favorites()

    def sync_all_favorite_sites(self, args: Dict = None) -> Dict[str, Any]:
        """Route to favorite sites sync - all sources"""
        return self.favorite_sites.sync_all_favorite_sites()

    def sync_stashdb_sites(self, args: Dict = None) -> Dict[str, Any]:
        """Route to favorite sites sync - StashDB only"""
        return self.favorite_sites.sync_stashdb_sites()

    def sync_tpdb_sites(self, args: Dict = None) -> Dict[str, Any]:
        """Route to favorite sites sync - TPDB only"""
        return self.favorite_sites.sync_tpdb_sites()

    def sync_fansdb_sites(self, args: Dict = None) -> Dict[str, Any]:
        """Route to favorite sites sync - FansDB only"""
        return self.favorite_sites.sync_fansdb_sites()

def main():
    """Main entry point for the plugin"""
    try:
        server_connection = None
        
        # Parse command line arguments or JSON input
        if len(sys.argv) > 1:
            mode = sys.argv[1]
            args = {"mode": mode}  # Convert to dict for consistency
        else:
            # Try to read from stdin for JSON input
            try:
                json_input = json.loads(sys.stdin.read())
                server_connection = json_input.get("server_connection")
                mode = json_input.get('args', {}).get('mode', 'update_all_performers')
                args = json_input.get('args', {})
                log.debug(f"Received JSON input with server_connection: {'Yes' if server_connection else 'No'}")
            except (json.JSONDecodeError, AttributeError):
                mode = 'update_all_performers'
                args = {}

        # Initialize plugin with server connection
        plugin = PerformerSiteSyncPlugin(server_connection)

        log.info(f"Starting Performer/Site Sync - Mode: {mode}")

        # Route to appropriate function based on mode
        if mode == 'test_connections':
            results = plugin.test_connections()
            log.info(f"Connection test completed: {len(results)} sources tested")
            
        elif mode == 'validate_config':
            results = plugin.validate_config()
            log.info(f"Configuration validation completed: {'Valid' if results.get('valid') else 'Invalid'}")
            
        elif mode == 'clear_cache':
            results = plugin.clear_cache()
            log.info(f"Cache cleared: {results}")
            
        elif mode == 'generate_sync_report':
            results = plugin.generate_sync_report()
            log.info("Sync report generated successfully")
            
        elif mode == 'update_all_performers':
            results = plugin.update_all_performers(args)
            log.info(f"Performer update completed: {results.get('updated', 0)} updated out of {results.get('total', 0)}")
            
        elif mode == 'update_single_performer':
            results = plugin.update_single_performer(args)
            log.info(f"Single performer update: {'Success' if results.get('updated') else 'No changes'}")
            
        elif mode == 'sync_all_favorites':
            results = plugin.sync_all_favorites(args)
            log.info(f"Favorite performers sync completed: {results.get('total_synced', 0)} synced")
            
        elif mode == 'sync_stashdb_favorites':
            results = plugin.sync_stashdb_favorites(args)
            log.info(f"StashDB favorites sync: {results.get('synced', 0)} synced")
            
        elif mode == 'sync_tpdb_favorites':
            results = plugin.sync_tpdb_favorites(args)
            log.info(f"TPDB favorites sync: {results.get('synced', 0)} synced")
            
        elif mode == 'sync_fansdb_favorites':
            results = plugin.sync_fansdb_favorites(args)
            log.info(f"FansDB favorites sync: {results.get('synced', 0)} synced")
            
        elif mode == 'sync_all_favorite_sites':
            results = plugin.sync_all_favorite_sites(args)
            log.info(f"Favorite sites sync completed: {results.get('total_synced', 0)} synced")
            
        elif mode == 'sync_stashdb_sites':
            results = plugin.sync_stashdb_sites(args)
            log.info(f"StashDB sites sync: {results.get('synced', 0)} synced")
            
        elif mode == 'sync_tpdb_sites':
            results = plugin.sync_tpdb_sites(args)
            log.info(f"TPDB sites sync: {results.get('synced', 0)} synced")
            
        elif mode == 'sync_fansdb_sites':
            results = plugin.sync_fansdb_sites(args)
            log.info(f"FansDB sites sync: {results.get('synced', 0)} synced")
            
        else:
            log.error(f"Unknown mode: {mode}")
            sys.exit(1)

        log.info("Performer/Site Sync completed successfully")

    except Exception as e:
        log.error(f"Performer/Site Sync failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
