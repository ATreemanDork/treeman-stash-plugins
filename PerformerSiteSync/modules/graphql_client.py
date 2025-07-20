"""
GraphQL Client Module
Handles all GraphQL requests, caching, and rate limiting
"""

import requests
import stashapi.log as log
import time
import json
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from .config import ConfigManager


class GraphQLClient:
    """Centralized GraphQL client with caching and rate limiting"""
    
    # GraphQL query definitions
    SEARCH_PERFORMER_QUERY = """
    query SearchPerformer($term: String!) {
        searchPerformer(term: $term) {
            id
            name
        }
    }
    """

    FIND_PERFORMER_QUERY = """
    query FindPerformer($id: ID!) {
        findPerformer(id: $id) {
            id
            name
            disambiguation
            aliases
            gender
            birth_date
            age
            ethnicity
            country
            eye_color
            hair_color
            height
            cup_size
            band_size
            waist_size
            hip_size
            breast_type
            career_start_year
            career_end_year
            deleted
            scene_count
            merged_ids
            is_favorite
            created
            updated
            images {
                id
                url
            }
        }
    }
    """

    FAVORITES_QUERY = """
    query {
        me {
            favorites {
                performers {
                    id
                    name
                    is_favorite
                }
            }
        }
    }
    """

    FAVORITE_SITES_QUERY = """
    query {
        me {
            favorites {
                sites {
                    id
                    name
                    url
                }
            }
        }
    }
    """

    TEST_QUERY = """
    query {
        __typename
    }
    """

    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.cache_db_path = self._get_cache_path()
        self._init_cache_database()
    
    def _get_cache_path(self) -> str:
        """Get cache database path"""
        plugin_dir = Path(__file__).parent.parent
        cache_dir = plugin_dir / "cache"
        cache_dir.mkdir(exist_ok=True)
        return str(cache_dir / "performer_sync_cache.db")

    def _init_cache_database(self):
        """Initialize SQLite cache database"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS performer_cache (
                        id TEXT PRIMARY KEY,
                        source TEXT,
                        performer_id TEXT,
                        data TEXT,
                        timestamp REAL
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS search_cache (
                        id TEXT PRIMARY KEY,
                        source TEXT,
                        search_term TEXT,
                        data TEXT,
                        timestamp REAL
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS favorites_cache (
                        id TEXT PRIMARY KEY,
                        source TEXT,
                        cache_type TEXT,
                        data TEXT,
                        timestamp REAL
                    )
                """)
                conn.commit()
        except Exception as e:
            log.error(f"Failed to initialize cache database: {e}")

    def _get_cache_key(self, source: str, operation: str, identifier: str) -> str:
        """Generate cache key"""
        return hashlib.md5(f"{source}:{operation}:{identifier}".encode()).hexdigest()

    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cache entry is still valid"""
        expiration_hours = self.config.plugin_config["cacheExpirationHours"]
        expiration_time = timestamp + (expiration_hours * 3600)
        return time.time() < expiration_time

    def _get_cached_data(self, cache_key: str, table: str = "performer_cache") -> Optional[Dict]:
        """Retrieve data from cache if valid"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT data, timestamp FROM {table} WHERE id = ?", (cache_key,))
                result = cursor.fetchone()
                
                if result:
                    data_json, timestamp = result
                    if self._is_cache_valid(timestamp):
                        return json.loads(data_json)
                    else:
                        # Remove expired cache entry
                        cursor.execute(f"DELETE FROM {table} WHERE id = ?", (cache_key,))
                        conn.commit()
                        
        except Exception as e:
            if self.config.plugin_config["debugLogging"]:
                log.error(f"Cache retrieval error: {e}")
                
        return None

    def _cache_data(self, cache_key: str, source: str, identifier: str, data: Dict, table: str = "performer_cache"):
        """Store data in cache"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                
                if table == "favorites_cache":
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO {table} 
                        (id, source, cache_type, data, timestamp) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (cache_key, source, identifier, json.dumps(data), time.time()))
                else:
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO {table} 
                        (id, source, performer_id, data, timestamp) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (cache_key, source, identifier, json.dumps(data), time.time()))
                    
                conn.commit()
        except Exception as e:
            if self.config.plugin_config["debugLogging"]:
                log.error(f"Cache storage error: {e}")

    def make_request(self, query: str, variables: Dict, source: str, use_cache: bool = True, retries: int = 5) -> Optional[Dict]:
        """Make GraphQL request with caching and rate limiting"""
        source_config = self.config.get_source_config(source)
        if not source_config:
            log.error(f"Source {source} not configured")
            return None
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(source, "request", str(hash(query + str(variables))))
            cached_data = self._get_cached_data(cache_key, "search_cache")
            if cached_data:
                if self.config.plugin_config["debugLogging"]:
                    log.debug(f"Cache hit for {source} request")
                return cached_data
        
        # Make the request
        headers = {'Content-Type': 'application/json'}
        api_key = source_config.get('api_key')
        if api_key:
            headers['Apikey'] = api_key
            
        for attempt in range(retries):
            try:
                # Rate limiting
                rate_limit = self.config.plugin_config["rateLimit"]
                if rate_limit > 0:
                    time.sleep(rate_limit)
                    
                response = requests.post(
                    source_config['url'], 
                    json={'query': query, 'variables': variables}, 
                    headers=headers
                )
                response.raise_for_status()
                response_json = response.json()
                
                if 'errors' in response_json:
                    log.error(f"GraphQL request returned errors: {response_json['errors']}")
                    return None
                    
                data = response_json.get('data')
                
                # Cache the result
                if use_cache and data:
                    cache_key = self._get_cache_key(source, "request", str(hash(query + str(variables))))
                    self._cache_data(cache_key, source, "request", data, "search_cache")
                
                return data
                
            except requests.exceptions.RequestException as e:
                log.error(f"GraphQL request failed (attempt {attempt + 1} of {retries}): {e}")
                if attempt < retries - 1:
                    sleep_time = 2 ** attempt
                    log.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    log.error("Max retries reached. Giving up.")
                    break
        
        return None

    def search_performer(self, search_term: str, source: str) -> Optional[List[Dict]]:
        """Search for performers by name"""
        data = self.make_request(self.SEARCH_PERFORMER_QUERY, {'term': search_term}, source)
        if data:
            return data.get('searchPerformer', [])
        return None

    def find_performer(self, performer_id: str, source: str) -> Optional[Dict]:
        """Find performer by ID"""
        # Check cache first for performer data
        cache_key = self._get_cache_key(source, "performer", performer_id)
        cached_data = self._get_cached_data(cache_key, "performer_cache")
        if cached_data:
            if self.config.plugin_config["debugLogging"]:
                log.debug(f"Cache hit for {source} performer {performer_id}")
            return cached_data

        data = self.make_request(self.FIND_PERFORMER_QUERY, {'id': performer_id}, source, use_cache=False)
        if data:
            performer_data = data.get('findPerformer')
            if performer_data:
                # Cache performer data specifically
                self._cache_data(cache_key, source, performer_id, performer_data, "performer_cache")
            return performer_data
        return None

    def get_favorites(self, source: str, favorite_type: str = "performers") -> Optional[List[Dict]]:
        """Get favorite performers or sites"""
        # Check cache first
        cache_key = self._get_cache_key(source, "favorites", favorite_type)
        cached_data = self._get_cached_data(cache_key, "favorites_cache")
        if cached_data:
            if self.config.plugin_config["debugLogging"]:
                log.debug(f"Cache hit for {source} {favorite_type} favorites")
            return cached_data

        # Choose appropriate query
        query = self.FAVORITES_QUERY if favorite_type == "performers" else self.FAVORITE_SITES_QUERY
        
        data = self.make_request(query, {}, source, use_cache=False)
        if data and data.get('me', {}).get('favorites'):
            favorites_data = data['me']['favorites'].get(favorite_type, [])
            # Cache favorites data
            self._cache_data(cache_key, source, favorite_type, favorites_data, "favorites_cache")
            return favorites_data
        return None

    def test_connection(self, source: str) -> Dict[str, Any]:
        """Test connection to a specific source"""
        result = {
            "source": source,
            "status": "unknown",
            "response_time": None,
            "error": None
        }
        
        source_config = self.config.get_source_config(source)
        if not source_config:
            result["status"] = "error"
            result["error"] = "Source not configured"
            return result
            
        result["endpoint"] = source_config['url']
        
        try:
            start_time = time.time()
            
            response_data = self.make_request(self.TEST_QUERY, {}, source, use_cache=False, retries=1)
            
            end_time = time.time()
            result["response_time"] = round((end_time - start_time) * 1000, 2)  # ms
            
            if response_data is not None:
                result["status"] = "connected"
            else:
                result["status"] = "failed"
                result["error"] = "No response data"
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            
        return result

    def clear_cache(self) -> Dict[str, int]:
        """Clear all cached data"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM performer_cache")
                performer_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM search_cache")
                search_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM favorites_cache")
                favorites_count = cursor.fetchone()[0]
                
                cursor.execute("DELETE FROM performer_cache")
                cursor.execute("DELETE FROM search_cache") 
                cursor.execute("DELETE FROM favorites_cache")
                conn.commit()
                
                return {
                    "performer_cache_cleared": performer_count,
                    "search_cache_cleared": search_count,
                    "favorites_cache_cleared": favorites_count
                }
                
        except Exception as e:
            log.error(f"Failed to clear cache: {e}")
            return {"error": str(e)}
