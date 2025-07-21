"""
Performer Sync Module
Handles performer data synchronization from external sources
Task 1: Update performers using existing IDs and optional name searches
"""

import stashapi.log as log
from typing import Dict, List, Optional, Any
from .config import ConfigManager
from .graphql_client import GraphQLClient
from .utils import DataUtils


class PerformerSync:
    """Handles performer data synchronization operations"""
    
    def __init__(self, config_manager: ConfigManager, graphql_client: GraphQLClient):
        self.config = config_manager
        self.graphql = graphql_client
        self.stash = config_manager.stash  # Use the authenticated StashInterface from ConfigManager
        
    def update_all_performers(self, enable_name_search: bool = None) -> Dict[str, Any]:
        """Update all performers in the library with data from external sources"""
        log.info("Starting update of all performers")
        
        # Use plugin setting if not specified
        if enable_name_search is None:
            enable_name_search = self.config.plugin_config.get("enableNameSearch", True)
        
        try:
            performers = self._get_all_performers()
            total_performers = len(performers)
            
            if total_performers == 0:
                log.info("No performers found in library")
                return {"processed": 0, "total": 0, "updated": 0, "errors": []}
            
            log.info(f"Found {total_performers} performers to process")
            
            processed_count = 0
            updated_count = 0
            errors = []
            
            for performer in performers:
                try:
                    result = self.update_performer_data(performer, enable_name_search)
                    if result.get("updated"):
                        updated_count += 1
                    
                    # Update progress
                    processed_count += 1
                    progress_percentage = processed_count / total_performers
                    log.progress(progress_percentage)
                    
                    sources_used = result.get("sources_used", [])
                    sources_str = ", ".join(DataUtils.normalize_source_name(s) for s in sources_used) if sources_used else "none"
                    log.info(f"Processed {processed_count}/{total_performers} performers ({progress_percentage*100:.1f}%) - {performer['name']} (sources: {sources_str})")
                    
                except Exception as e:
                    error_msg = f"Error processing performer {performer.get('name', 'Unknown')} (ID: {performer.get('id', 'Unknown')}): {str(e)}"
                    errors.append(error_msg)
                    log.error(error_msg)
                    processed_count += 1
            
            summary = DataUtils.generate_sync_summary(processed_count, total_performers, [], errors)
            log.info(f"Completed performer update: {summary}")
            
            return {
                "processed": processed_count,
                "total": total_performers,
                "updated": updated_count,
                "errors": errors
            }
            
        except Exception as e:
            log.error(f"Failed to update all performers: {str(e)}")
            return {"error": str(e)}

    def update_single_performer(self, performer_id: str, enable_name_search: bool = None) -> Dict[str, Any]:
        """Update a single performer by ID"""
        log.info(f"Updating single performer with ID: {performer_id}")
        
        # Use plugin setting if not specified
        if enable_name_search is None:
            enable_name_search = self.config.plugin_config.get("enableNameSearch", True)
        
        try:
            performer = self._find_local_performer(performer_id)
            if not performer:
                error_msg = f"Performer with ID {performer_id} not found"
                log.error(error_msg)
                return {"error": error_msg}
            
            result = self.update_performer_data(performer, enable_name_search)
            return result
            
        except Exception as e:
            log.error(f"Failed to update performer {performer_id}: {str(e)}")
            return {"error": str(e)}

    def update_performer_data(self, performer: Dict, enable_name_search: bool = True) -> Dict[str, Any]:
        """Main function to update performer data from external sources"""
        performer_name = performer.get('name', 'Unknown')
        performer_id = performer.get('id', 'Unknown')
        
        log.info(f"Processing performer: {performer_name} (ID: {performer_id})")

        # Get existing stash_ids
        existing_stash_ids_by_source = DataUtils.get_existing_stash_ids(performer, self.config.sources)
        performer_data_by_source = {}
        
        # Get source precedence list
        source_precedence = DataUtils.get_source_precedence_list(self.config.sources)
        
        # Process each enabled source
        for source in self.config.get_enabled_sources():
            try:
                if source in existing_stash_ids_by_source:
                    # Direct lookup by existing stash_id (much faster)
                    stash_id = existing_stash_ids_by_source[source]
                    log.debug(f"Fetching {source} data by existing stash_id: {stash_id}")
                    
                    performer_data = self.graphql.find_performer(stash_id, source)
                    if performer_data:
                        performer_data_by_source[source] = performer_data
                        log.debug(f"Successfully fetched {source} data by stash_id")
                    else:
                        log.warning(f"Failed to fetch {source} data for stash_id: {stash_id}")
                        
                elif enable_name_search:
                    # Search by name for missing stash_ids
                    log.debug(f"Searching {source} by name: {performer_name}")
                    performer_data = self._search_and_match_performer(performer_name, source)
                    if performer_data:
                        performer_data_by_source[source] = performer_data
                        log.debug(f"Successfully found {source} match by name")
                else:
                    log.debug(f"Skipping name search for {source} (disabled)")
                    
            except Exception as e:
                log.error(f"Error processing {source} for performer {performer_name}: {str(e)}")
                continue
        
        # Check if we have any data to work with
        if not performer_data_by_source:
            log.info(f"No new details found for performer {performer_name} (ID: {performer_id}) - already up to date or no matches found")
            return {
                "updated": False,
                "performer_id": performer_id,
                "performer_name": performer_name,
                "sources_used": [],
                "message": "No new data found"
            }
        
        # Merge data from all sources with precedence
        combined_data = DataUtils.merge_performer_data(performer_data_by_source, source_precedence)
        
        # Extract image URL with precedence
        image_url = None
        if self.config.plugin_config.get("performerImageUpdate", True):
            image_url = DataUtils.extract_image_url(performer_data_by_source, source_precedence)
        
        # Build complete stash_ids list
        combined_stash_ids = DataUtils.build_stash_ids_list(
            performer.get('stash_ids', []), 
            performer_data_by_source, 
            self.config.sources
        )
        
        # Prepare update data
        performer_update_data = DataUtils.build_performer_update_data(
            combined_data, performer, image_url, combined_stash_ids
        )

        log.debug(f"Prepared performer update data: {performer_update_data}")

        try:
            update_result = self._update_performer(performer_update_data, performer_id)
            if update_result:
                sources_used = list(performer_data_by_source.keys())
                sources_str = ", ".join(DataUtils.normalize_source_name(s) for s in sources_used)
                log.info(f"Updated performer: {update_result['name']} (ID: {update_result['id']}) with data from: {sources_str}")
                
                return {
                    "updated": True,
                    "performer_id": performer_id,
                    "performer_name": update_result['name'],
                    "sources_used": sources_used,
                    "message": f"Updated with data from {sources_str}"
                }
            else:
                log.warning(f"Update operation returned no result for performer {performer_name} (ID: {performer_id})")
                return {
                    "updated": False,
                    "performer_id": performer_id,
                    "performer_name": performer_name,
                    "sources_used": list(performer_data_by_source.keys()),
                    "message": "Update operation failed"
                }
                
        except Exception as e:
            log.error(f"Failed to update performer: {performer_name} (ID: {performer_id}) - {str(e)}")
            return {
                "updated": False,
                "performer_id": performer_id,
                "performer_name": performer_name,
                "sources_used": list(performer_data_by_source.keys()),
                "error": str(e)
            }

    def _search_and_match_performer(self, performer_name: str, source: str) -> Optional[Dict]:
        """Search for performer by name and return exact match if found"""
        search_results = self.graphql.search_performer(performer_name, source)
        if not search_results:
            log.debug(f"No search results found on {source} for: {performer_name}")
            return None
        
        # Find exact name matches
        exact_matches = DataUtils.find_exact_matches(search_results, performer_name)
        
        if len(exact_matches) == 1:
            # Fetch full data for the matched performer
            return self.graphql.find_performer(exact_matches[0]['id'], source)
        elif len(exact_matches) > 1:
            log.info(f"Skipped performer {performer_name} due to multiple exact matches on {source}")
            return None
        else:
            log.debug(f"No exact match found on {source} for: {performer_name}")
            return None

    def _get_all_performers(self) -> List[Dict]:
        """Get all performers from local Stash"""
        try:
            response = self.stash.find_performers()
            if response:
                return response
            return []
        except Exception as e:
            log.error(f"Failed to get performers from Stash: {str(e)}")
            return []

    def _find_local_performer(self, performer_id: str) -> Optional[Dict]:
        """Find a specific performer in local Stash"""
        try:
            response = self.stash.find_performer(performer_id)
            if response:
                return response
            return None
        except Exception as e:
            log.error(f"Failed to find performer {performer_id} in Stash: {str(e)}")
            return None

    def _update_performer(self, performer_data: Dict, performer_id: str) -> Optional[Dict]:
        """Update local performer with new data"""
        performer_data['id'] = performer_id

        # Convert date to string if it's a datetime object
        if hasattr(performer_data.get('birthdate'), 'strftime'):
            performer_data['birthdate'] = performer_data['birthdate'].strftime('%Y-%m-%d')

        try:
            response = self.stash.update_performer(performer_data)
            return response
        except Exception as e:
            log.error(f"Failed to update performer {performer_id}: {e}")
            return None

    def get_performer_statistics(self) -> Dict[str, Any]:
        """Get statistics about performers and their external source coverage"""
        try:
            performers = self._get_all_performers()
            total_performers = len(performers)
            
            stats = {
                "total_performers": total_performers,
                "source_coverage": {},
                "performers_with_stash_ids": 0,
                "performers_without_stash_ids": 0
            }
            
            # Initialize source coverage counters
            for source in self.config.get_enabled_sources():
                stats["source_coverage"][source] = 0
            
            for performer in performers:
                existing_stash_ids = DataUtils.get_existing_stash_ids(performer, self.config.sources)
                
                if existing_stash_ids:
                    stats["performers_with_stash_ids"] += 1
                    for source in existing_stash_ids.keys():
                        if source in stats["source_coverage"]:
                            stats["source_coverage"][source] += 1
                else:
                    stats["performers_without_stash_ids"] += 1
            
            return stats
            
        except Exception as e:
            log.error(f"Failed to get performer statistics: {str(e)}")
            return {"error": str(e)}
