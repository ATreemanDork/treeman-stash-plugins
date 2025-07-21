"""
Favorite Performers Module
Handles synchronization of favorite performers from external sources
Task 2: Sync favorite performers from StashDB, TPDB, FansDB
"""

import stashapi.log as log
from typing import Dict, List, Optional, Any
from .config import ConfigManager
from .graphql_client import GraphQLClient
from .utils import DataUtils


class FavoritePerformers:
    """Handles favorite performer synchronization operations"""
    
    def __init__(self, config_manager: ConfigManager, graphql_client: GraphQLClient):
        self.config = config_manager
        self.graphql = graphql_client
        self.stash = config_manager.stash  # Use the authenticated StashInterface from ConfigManager
        
    def sync_all_favorites(self) -> Dict[str, Any]:
        """Sync favorite performers from all enabled sources"""
        log.info("Starting sync of favorite performers from all sources")
        
        results = {}
        total_synced = 0
        total_created = 0
        total_errors = 0
        
        for source in self.config.get_enabled_sources():
            try:
                result = self._sync_source_favorites(source)
                results[source] = result
                total_synced += result.get("synced", 0)
                total_created += result.get("created", 0)
                total_errors += len(result.get("errors", []))
            except Exception as e:
                error_msg = f"Failed to sync {source} favorites: {str(e)}"
                log.error(error_msg)
                results[source] = {"error": error_msg}
                total_errors += 1
        
        log.info(f"Completed sync of all favorite performers: {total_synced} synced, {total_created} created, {total_errors} errors")
        
        return {
            "total_synced": total_synced,
            "total_created": total_created,
            "total_errors": total_errors,
            "source_results": results
        }
    
    def sync_stashdb_favorites(self) -> Dict[str, Any]:
        """Sync favorite performers from StashDB"""
        return self._sync_source_favorites("stashdb")
    
    def sync_tpdb_favorites(self) -> Dict[str, Any]:
        """Sync favorite performers from ThePornDB"""
        return self._sync_source_favorites("tpdb")
    
    def sync_fansdb_favorites(self) -> Dict[str, Any]:
        """Sync favorite performers from FansDB"""
        return self._sync_source_favorites("fansdb")
    
    def _sync_source_favorites(self, source: str) -> Dict[str, Any]:
        """Sync favorite performers from a specific source"""
        source_name = DataUtils.normalize_source_name(source)
        log.info(f"Syncing favorite performers from {source_name}")
        
        if not self.config.is_source_enabled(source):
            error_msg = f"Source {source_name} is not enabled"
            log.error(error_msg)
            return {"error": error_msg}
        
        try:
            # Get favorites from external source
            favorites = self.graphql.get_favorites(source, "performers")
            if not favorites:
                log.info(f"No favorite performers found on {source_name}")
                return {"synced": 0, "errors": [], "message": "No favorites found"}
            
            log.info(f"Found {len(favorites)} favorite performers on {source_name}")
            
            synced_count = 0
            created_count = 0
            errors = []
            
            for favorite in favorites:
                try:
                    result = self._sync_favorite_performer(favorite, source)
                    if result.get("synced"):
                        synced_count += 1
                    if result.get("created"):
                        created_count += 1
                    if result.get("error"):
                        errors.append(result["error"])
                        
                except Exception as e:
                    error_msg = f"Error syncing favorite {favorite.get('name', 'Unknown')}: {str(e)}"
                    errors.append(error_msg)
                    log.error(error_msg)
            
            log.info(f"Synced {synced_count}/{len(favorites)} favorite performers from {source_name} ({created_count} created)")
            
            return {
                "synced": synced_count,
                "created": created_count,
                "total": len(favorites),
                "errors": errors,
                "source": source_name
            }
            
        except Exception as e:
            error_msg = f"Failed to sync favorites from {source_name}: {str(e)}"
            log.error(error_msg)
            return {"error": error_msg}
    
    def _sync_favorite_performer(self, favorite: Dict, source: str) -> Dict[str, Any]:
        """Sync a single favorite performer to local Stash"""
        performer_name = favorite.get('name', 'Unknown')
        performer_id = favorite.get('id', 'Unknown')
        
        try:
            # Try to find local performer by stash_id first
            local_performer = self._find_local_performer_by_stash_id(performer_id, source)
            
            if not local_performer:
                # Try to find by name
                local_performer = self._find_local_performer_by_name(performer_name)
            
            if not local_performer:
                # Auto-create if enabled
                if self.config.plugin_config.get("autoCreatePerformers", False):
                    local_performer = self._create_local_performer(performer_name, performer_id, source)
                    if local_performer:
                        log.info(f"Auto-created and marked performer {performer_name} as favorite")
                        return {"synced": True, "created": True}
                    else:
                        error_msg = f"Failed to auto-create performer {performer_name}"
                        log.error(error_msg)
                        return {"synced": False, "error": error_msg}
                else:
                    log.info(f"Performer {performer_name} not found locally, auto-creation disabled")
                    return {
                        "synced": False,
                        "error": f"Performer {performer_name} not found locally (auto-creation disabled)"
                    }
            
            # Check if already favorited
            if local_performer.get('favorite'):
                log.debug(f"Performer {performer_name} is already marked as favorite")
                return {"synced": False, "message": "Already favorite"}
            
            # Mark as favorite
            success = self._mark_performer_favorite(local_performer['id'], True)
            if success:
                log.info(f"Marked performer {performer_name} as favorite")
                return {"synced": True}
            else:
                error_msg = f"Failed to mark {performer_name} as favorite"
                log.error(error_msg)
                return {"synced": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error processing favorite {performer_name}: {str(e)}"
            log.error(error_msg)
            return {"synced": False, "error": error_msg}
    
    def _find_local_performer_by_stash_id(self, stash_id: str, source: str) -> Optional[Dict]:
        """Find local performer by external stash_id"""
        try:
            performers = self.stash.find_performers()
            source_config = self.config.get_source_config(source)
            if not source_config:
                return None
            
            source_endpoint = source_config['url']
            
            for performer in performers:
                for existing_stash_id in performer.get('stash_ids', []):
                    if (existing_stash_id.get('endpoint') == source_endpoint and 
                        existing_stash_id.get('stash_id') == stash_id):
                        return performer
            
            return None
            
        except Exception as e:
            log.error(f"Error finding performer by stash_id {stash_id}: {str(e)}")
            return None
    
    def _find_local_performer_by_name(self, name: str) -> Optional[Dict]:
        """Find local performer by name (exact match)"""
        try:
            performers = self.stash.find_performers()
            for performer in performers:
                if performer.get('name', '').lower() == name.lower():
                    return performer
            return None
            
        except Exception as e:
            log.error(f"Error finding performer by name {name}: {str(e)}")
            return None
    
    def _mark_performer_favorite(self, performer_id: str, favorite: bool = True) -> bool:
        """Mark performer as favorite in local Stash"""
        try:
            update_data = {
                'id': performer_id,
                'favorite': favorite
            }
            
            result = self.stash.update_performer(update_data)
            return result is not None
            
        except Exception as e:
            log.error(f"Error marking performer {performer_id} as favorite: {str(e)}")
            return False
    
    def _create_local_performer(self, name: str, stash_id: str, source: str) -> Optional[Dict]:
        """Create a new performer with minimal required fields"""
        try:
            # Get source endpoint URL for stash_id
            source_config = self.config.get_source_config(source)
            if not source_config:
                log.error(f"No configuration found for source: {source}")
                return None
            
            source_endpoint = source_config['url']
            
            # Create performer with minimum required fields
            create_data = {
                'name': name,
                'favorite': True,  # Set as favorite since they're being imported
                'stash_ids': [{
                    'endpoint': source_endpoint,
                    'stash_id': stash_id
                }]
            }
            
            log.info(f"Creating new performer: {name}")
            result = self.stash.create_performer(create_data)
            
            if result and result.get('id'):
                log.info(f"Successfully created performer {name} with ID: {result['id']}")
                return result
            else:
                log.error(f"Failed to create performer {name}: No ID returned")
                return None
            
        except Exception as e:
            log.error(f"Error creating performer {name}: {str(e)}")
            return None
    
    def get_favorite_statistics(self) -> Dict[str, Any]:
        """Get statistics about favorite performers"""
        try:
            performers = self.stash.find_performers()
            total_performers = len(performers)
            favorite_performers = sum(1 for p in performers if p.get('favorite'))
            
            # Count performers with external stash_ids
            performers_with_external_ids = 0
            source_coverage = {}
            
            for source in self.config.get_enabled_sources():
                source_coverage[source] = 0
            
            for performer in performers:
                existing_stash_ids = DataUtils.get_existing_stash_ids(performer, self.config.sources)
                if existing_stash_ids:
                    performers_with_external_ids += 1
                    for source in existing_stash_ids.keys():
                        if source in source_coverage:
                            source_coverage[source] += 1
            
            return {
                "total_performers": total_performers,
                "favorite_performers": favorite_performers,
                "performers_with_external_ids": performers_with_external_ids,
                "source_coverage": source_coverage
            }
            
        except Exception as e:
            log.error(f"Failed to get favorite statistics: {str(e)}")
            return {"error": str(e)}
