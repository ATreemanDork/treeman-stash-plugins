"""
Favorite Sites Module
Handles syncing favorite sites/studios from external sources
Tasks 5-7: Sync favorite sites from StashDB, TPDB, FansDB
"""

import stashapi.log as log
from typing import Dict, List, Optional, Any
from .config import ConfigManager
from .graphql_client import GraphQLClient
from .utils import DataUtils


class FavoriteSites:
    """Handles favorite site/studio synchronization operations"""
    
    def __init__(self, config_manager: ConfigManager, graphql_client: GraphQLClient):
        self.config = config_manager
        self.graphql = graphql_client
        self.stash = config_manager.stash  # Use the authenticated StashInterface from ConfigManager
        
    def sync_all_favorite_sites(self) -> Dict[str, Any]:
        """Sync favorite sites from all enabled sources"""
        log.info("Starting sync of favorite sites from all sources")
        
        results = {}
        total_synced = 0
        total_errors = 0
        
        for source in self.config.get_enabled_sources():
            try:
                result = self._sync_source_favorite_sites(source)
                results[source] = result
                total_synced += result.get("synced", 0)
                total_errors += len(result.get("errors", []))
            except Exception as e:
                error_msg = f"Failed to sync {source} favorite sites: {str(e)}"
                log.error(error_msg)
                results[source] = {"error": error_msg}
                total_errors += 1
        
        log.info(f"Completed sync of all favorite sites: {total_synced} synced, {total_errors} errors")
        
        return {
            "total_synced": total_synced,
            "total_errors": total_errors,
            "source_results": results
        }
    
    def sync_stashdb_sites(self) -> Dict[str, Any]:
        """Sync favorite sites from StashDB"""
        return self._sync_source_favorite_sites("stashdb")
    
    def sync_tpdb_sites(self) -> Dict[str, Any]:
        """Sync favorite sites from ThePornDB"""
        return self._sync_source_favorite_sites("tpdb")
    
    def sync_fansdb_sites(self) -> Dict[str, Any]:
        """Sync favorite sites from FansDB"""
        return self._sync_source_favorite_sites("fansdb")
    
    def _sync_source_favorite_sites(self, source: str) -> Dict[str, Any]:
        """Sync favorite sites from a specific source"""
        source_name = DataUtils.normalize_source_name(source)
        log.info(f"Syncing favorite sites from {source_name}")
        
        if not self.config.is_source_enabled(source):
            error_msg = f"Source {source_name} is not enabled"
            log.error(error_msg)
            return {"error": error_msg}
        
        try:
            # Get favorite sites from external source
            favorites = self.graphql.get_favorites(source, "sites")
            if not favorites:
                log.info(f"No favorite sites found on {source_name}")
                return {"synced": 0, "errors": [], "message": "No favorites found"}
            
            log.info(f"Found {len(favorites)} favorite sites on {source_name}")
            
            synced_count = 0
            created_count = 0
            errors = []
            
            for favorite in favorites:
                try:
                    result = self._sync_favorite_site(favorite, source)
                    if result.get("synced"):
                        synced_count += 1
                    if result.get("created"):
                        created_count += 1
                    if result.get("error"):
                        errors.append(result["error"])
                        
                except Exception as e:
                    error_msg = f"Error syncing favorite site {favorite.get('name', 'Unknown')}: {str(e)}"
                    errors.append(error_msg)
                    log.error(error_msg)
            
            log.info(f"Synced {synced_count}/{len(favorites)} favorite sites from {source_name} ({created_count} created)")
            
            return {
                "synced": synced_count,
                "created": created_count,
                "total": len(favorites),
                "errors": errors,
                "source": source_name
            }
            
        except Exception as e:
            error_msg = f"Failed to sync favorite sites from {source_name}: {str(e)}"
            log.error(error_msg)
            return {"error": error_msg}
    
    def _sync_favorite_site(self, favorite: Dict, source: str) -> Dict[str, Any]:
        """Sync a single favorite site to local Stash"""
        site_name = favorite.get('name', 'Unknown')
        site_id = favorite.get('id', 'Unknown')
        site_url = favorite.get('url', '')
        
        try:
            # Try to find local studio by stash_id first
            local_studio = self._find_local_studio_by_stash_id(site_id, source)
            
            if not local_studio:
                # Try to find by name
                local_studio = self._find_local_studio_by_name(site_name)
            
            if not local_studio:
                # Auto-create if enabled
                if self.config.plugin_config.get("autoCreateSites", False):
                    local_studio = self._create_local_studio(site_name, site_url, site_id, source)
                    if local_studio:
                        log.info(f"Created new studio {site_name} and marked as favorite")
                        return {"synced": True, "created": True}
                    else:
                        error_msg = f"Failed to create studio {site_name}"
                        log.error(error_msg)
                        return {"synced": False, "error": error_msg}
                else:
                    log.info(f"Studio {site_name} not found locally and auto-creation is disabled")
                    return {
                        "synced": False,
                        "error": f"Studio {site_name} not found locally (auto-creation disabled)"
                    }
            
            # Check if already favorited
            if local_studio.get('favorite'):
                log.debug(f"Studio {site_name} is already marked as favorite")
                return {"synced": False, "message": "Already favorite"}
            
            # Mark as favorite
            success = self._mark_studio_favorite(local_studio['id'], True)
            if success:
                log.info(f"Marked studio {site_name} as favorite")
                return {"synced": True, "created": False}
            else:
                error_msg = f"Failed to mark {site_name} as favorite"
                log.error(error_msg)
                return {"synced": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error processing favorite site {site_name}: {str(e)}"
            log.error(error_msg)
            return {"synced": False, "error": error_msg}
    
    def _find_local_studio_by_stash_id(self, stash_id: str, source: str) -> Optional[Dict]:
        """Find local studio by external stash_id"""
        try:
            studios = self.stash.find_studios()
            source_config = self.config.get_source_config(source)
            if not source_config:
                return None
            
            source_endpoint = source_config['url']
            
            for studio in studios:
                for existing_stash_id in studio.get('stash_ids', []):
                    if (existing_stash_id.get('endpoint') == source_endpoint and 
                        existing_stash_id.get('stash_id') == stash_id):
                        return studio
            
            return None
            
        except Exception as e:
            log.error(f"Error finding studio by stash_id {stash_id}: {str(e)}")
            return None
    
    def _find_local_studio_by_name(self, name: str) -> Optional[Dict]:
        """Find local studio by name (exact match)"""
        try:
            studios = self.stash.find_studios()
            for studio in studios:
                if studio.get('name', '').lower() == name.lower():
                    return studio
            return None
            
        except Exception as e:
            log.error(f"Error finding studio by name {name}: {str(e)}")
            return None
    
    def _create_local_studio(self, name: str, url: str, external_id: str, source: str) -> Optional[Dict]:
        """Create a new studio in local Stash"""
        try:
            source_config = self.config.get_source_config(source)
            if not source_config:
                return None
            
            studio_data = {
                'name': name,
                'url': url,
                'favorite': True,  # Mark as favorite immediately
                'stash_ids': [{
                    'stash_id': external_id,
                    'endpoint': source_config['url']
                }]
            }
            
            result = self.stash.create_studio(studio_data)
            return result
            
        except Exception as e:
            log.error(f"Error creating studio {name}: {str(e)}")
            return None
    
    def _mark_studio_favorite(self, studio_id: str, favorite: bool = True) -> bool:
        """Mark studio as favorite in local Stash"""
        try:
            update_data = {
                'id': studio_id,
                'favorite': favorite
            }
            
            result = self.stash.update_studio(update_data)
            return result is not None
            
        except Exception as e:
            log.error(f"Error marking studio {studio_id} as favorite: {str(e)}")
            return False
    
    def get_studio_statistics(self) -> Dict[str, Any]:
        """Get statistics about studios"""
        try:
            studios = self.stash.find_studios()
            total_studios = len(studios)
            favorite_studios = sum(1 for s in studios if s.get('favorite'))
            
            # Count studios with external stash_ids
            studios_with_external_ids = 0
            source_coverage = {}
            
            for source in self.config.get_enabled_sources():
                source_coverage[source] = 0
            
            for studio in studios:
                has_external_id = False
                for stash_id in studio.get('stash_ids', []):
                    endpoint = stash_id.get('endpoint', '')
                    for source, config in self.config.sources.items():
                        if endpoint == config['url']:
                            if not has_external_id:
                                studios_with_external_ids += 1
                                has_external_id = True
                            if source in source_coverage:
                                source_coverage[source] += 1
                            break
            
            return {
                "total_studios": total_studios,
                "favorite_studios": favorite_studios,
                "studios_with_external_ids": studios_with_external_ids,
                "source_coverage": source_coverage
            }
            
        except Exception as e:
            log.error(f"Failed to get studio statistics: {str(e)}")
            return {"error": str(e)}
