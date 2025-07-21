"""
Data Utilities Module
Shared utilities for data processing, transformation, and helper functions
"""

import stashapi.log as log
from datetime import datetime
from typing import Dict, List, Optional, Any


class DataUtils:
    """Utility functions for data processing and transformation"""
    
    @staticmethod
    def parse_birthdate(date_str: str) -> Optional[datetime]:
        """Parse birth date string into datetime object"""
        if not date_str:
            return None
            
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%Y')
            except ValueError:
                log.warning(f"Could not parse date: {date_str}")
                return None

    @staticmethod
    def format_birthdate(date_obj: datetime) -> str:
        """Format datetime object as date string"""
        if isinstance(date_obj, datetime):
            return date_obj.strftime('%Y-%m-%d')
        return str(date_obj) if date_obj else None

    @staticmethod
    def get_existing_stash_ids(performer: Dict, sources_config: Dict) -> Dict[str, str]:
        """Extract existing stash_ids by source from performer data"""
        stash_ids_by_source = {}
        
        for stash_id in performer.get('stash_ids', []):
            endpoint = stash_id.get('endpoint', '')
            stash_id_value = stash_id.get('stash_id', '')
            
            # Map endpoint URLs to source names
            for source_name, source_config in sources_config.items():
                if endpoint == source_config['url']:
                    stash_ids_by_source[source_name] = stash_id_value
                    break
        
        return stash_ids_by_source

    @staticmethod
    def merge_performer_data(performer_data_by_source: Dict[str, Dict], source_precedence: List[str]) -> Dict:
        """Merge performer data from multiple sources with precedence"""
        combined_data = {}
        
        # Apply data in reverse precedence order (lowest to highest priority)
        for source in reversed(source_precedence):
            if source in performer_data_by_source and performer_data_by_source[source]:
                source_data = performer_data_by_source[source]
                combined_data.update(source_data)
                log.debug(f"Applied {source} data to combined performer data")
        
        return combined_data

    @staticmethod
    def extract_image_url(performer_data_by_source: Dict[str, Dict], source_precedence: List[str]) -> Optional[str]:
        """Extract image URL with source precedence"""
        for source in source_precedence:
            if source in performer_data_by_source and performer_data_by_source[source]:
                performer_data = performer_data_by_source[source]
                if isinstance(performer_data, dict):
                    images = performer_data.get('images', [])
                    if images and len(images) > 0:
                        image_url = images[0].get('url')
                        if image_url:
                            log.debug(f"Using image from {source}: {image_url}")
                            return image_url
        return None

    @staticmethod
    def build_stash_ids_list(existing_stash_ids: List[Dict], performer_data_by_source: Dict[str, Dict], sources_config: Dict) -> List[Dict]:
        """Build complete stash_ids list including existing and new ones"""
        stash_ids_list = list(existing_stash_ids) if existing_stash_ids else []
        
        # Add new stash_ids for sources that have data but no existing stash_id
        for source, performer_data in performer_data_by_source.items():
            if performer_data and performer_data.get('id'):
                source_endpoint = sources_config[source]['url']
                
                # Check if this stash_id already exists
                already_exists = any(
                    stash_id.get('endpoint') == source_endpoint and 
                    stash_id.get('stash_id') == performer_data['id']
                    for stash_id in stash_ids_list
                )
                
                if not already_exists:
                    stash_ids_list.append({
                        'stash_id': performer_data['id'],
                        'endpoint': source_endpoint
                    })
                    log.debug(f"Added new stash_id for {source}: {performer_data['id']}")
        
        return stash_ids_list

    @staticmethod
    def build_performer_update_data(combined_data: Dict, performer: Dict, image_url: Optional[str], stash_ids: List[Dict]) -> Dict:
        """Build performer update data structure for Stash API"""
        # Process combined data
        gender = combined_data.get('gender')
        if gender not in ['MALE', 'FEMALE']:
            gender = None
        
        alias_list = list(set(combined_data.get('aliases', [])))  # Remove duplicates
        birthdate = DataUtils.parse_birthdate(combined_data.get('birth_date'))
        
        # Build measurements string
        measurements = None
        cup_size = combined_data.get('cup_size', '')
        band_size = combined_data.get('band_size', '')
        waist_size = combined_data.get('waist_size', '')
        hip_size = combined_data.get('hip_size', '')
        
        if any([cup_size, band_size, waist_size, hip_size]):
            measurements = f"{cup_size}{band_size}-{waist_size}-{hip_size}"
        
        # Build career length string
        career_length = None
        start_year = combined_data.get('career_start_year', '')
        end_year = combined_data.get('career_end_year', '')
        
        if end_year:
            career_length = f"{start_year}-{end_year}"
        elif start_year:
            career_length = str(start_year)
        
        return {
            'name': combined_data.get('name', performer['name']),  # Fallback to original name
            'disambiguation': combined_data.get('disambiguation'),
            'alias_list': ', '.join(alias_list) if alias_list else None,
            'gender': gender,
            'birthdate': DataUtils.format_birthdate(birthdate),
            'ethnicity': combined_data.get('ethnicity'),
            'country': combined_data.get('country'),
            'eye_color': combined_data.get('eye_color'),
            'hair_color': combined_data.get('hair_color'),
            'height_cm': combined_data.get('height'),
            'measurements': measurements,
            'fake_tits': combined_data.get('breast_type'),
            'career_length': career_length,
            'details': None,
            'death_date': None,
            'weight': None,
            'twitter': None,
            'instagram': None,
            'image': image_url,
            'url': None,
            'tag_ids': None,
            'tattoos': None,
            'piercings': None,
            'stash_ids': stash_ids
        }

    @staticmethod
    def find_exact_matches(search_results: List[Dict], search_term: str) -> List[Dict]:
        """Find exact name matches from search results"""
        return [result for result in search_results if result['name'].lower() == search_term.lower()]

    @staticmethod
    def normalize_source_name(source: str) -> str:
        """Normalize source name for display"""
        name_mapping = {
            'stashdb': 'StashDB',
            'tpdb': 'ThePornDB',
            'fansdb': 'FansDB'
        }
        return name_mapping.get(source, source.title())

    @staticmethod
    def get_source_precedence_list(sources_config: Dict) -> List[str]:
        """Get list of sources ordered by precedence (highest first)"""
        return sorted(sources_config.keys(), key=lambda x: sources_config[x]['precedence'])

    @staticmethod
    def format_measurements(cup_size: str = "", band_size: str = "", waist_size: str = "", hip_size: str = "") -> Optional[str]:
        """Format measurements into standard string"""
        if any([cup_size, band_size, waist_size, hip_size]):
            return f"{cup_size}{band_size}-{waist_size}-{hip_size}"
        return None

    @staticmethod
    def format_career_length(start_year: Any = None, end_year: Any = None) -> Optional[str]:
        """Format career length into standard string"""
        start_str = str(start_year) if start_year else ""
        end_str = str(end_year) if end_year else ""
        
        if end_str:
            return f"{start_str}-{end_str}"
        elif start_str:
            return start_str
        return None

    @staticmethod
    def clean_alias_list(aliases: List[str]) -> List[str]:
        """Clean and deduplicate alias list"""
        if not aliases:
            return []
        
        # Remove duplicates and empty strings, strip whitespace
        cleaned = list(set(alias.strip() for alias in aliases if alias and alias.strip()))
        return sorted(cleaned)  # Sort for consistency

    @staticmethod
    def validate_gender(gender: str) -> Optional[str]:
        """Validate and normalize gender value"""
        if not gender:
            return None
        
        gender_upper = gender.upper()
        if gender_upper in ['MALE', 'FEMALE']:
            return gender_upper
        return None

    @staticmethod
    def safe_int_convert(value: Any) -> Optional[int]:
        """Safely convert value to integer"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def generate_sync_summary(processed_count: int, total_count: int, sources_used: List[str], errors: List[str] = None) -> str:
        """Generate a summary string for sync operations"""
        percentage = (processed_count / total_count * 100) if total_count > 0 else 0
        summary = f"Processed {processed_count}/{total_count} items ({percentage:.1f}%)"
        
        if sources_used:
            summary += f" using data from: {', '.join(DataUtils.normalize_source_name(s) for s in sources_used)}"
        
        if errors:
            summary += f" | {len(errors)} errors encountered"
            
        return summary
