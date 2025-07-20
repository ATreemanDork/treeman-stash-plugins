# Performer/Site Sync Plugin

A comprehensive Stash plugin for synchronizing performer data between your local Stash instance and external sources including StashDB, ThePornDB (TPDB), and FansDB.

## Features

### Manual Task Controls
- **Update All Performers**: Sync all performers in your library with external data (includes name search toggle)
- **Update Single Performer**: Update specific performers (works with performer page hooks)
- **Sync Favorite Performers**: Import favorite performers from external sources (All Sources + Individual)
- **Sync Favorite Sites**: Import favorite sites/studios from external sources (All Sources + Individual) 
- **Test Connections**: Verify connectivity to all configured endpoints
- **Clear Cache**: Force fresh data retrieval by clearing cached responses
- **Generate Reports**: Detailed sync status and statistics
- **Validate Configuration**: Check your endpoint setup and API keys

### Data Sources
- **StashDB**: Primary performer database with comprehensive information
- **ThePornDB (TPDB)**: Adult film database with performer details
- **FansDB**: Fan-maintained performer database

### Smart Features
- **Modular Architecture**: Clean separation of concerns across multiple Python modules
- **Intelligent Caching**: Reduces API calls with configurable cache expiration
- **Rate Limiting**: Prevents overwhelming external APIs
- **Source Precedence**: Configurable priority for merging conflicting data
- **Name Search Toggle**: Optional name-based searches when stash_ids are missing
- **Auto-Site Creation**: Optional automatic creation of missing sites/studios
- **Auto-Performer Creation**: Optional automatic creation of missing performers when syncing favorites
- **Error Recovery**: Automatic retry logic with exponential backoff
- **Progress Tracking**: Real-time progress updates for long operations

## Installation

1. **Copy Plugin Files**:
   ```
   plugins/PerformerSiteSync/
   ├── performer_site_sync.yml      # Plugin manifest
   ├── performer_site_sync.py       # Main Python script  
   ├── performer_site_sync.js       # UI enhancements
   ├── requirements.txt             # Python dependencies
   └── README.md                    # This file
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure External Sources**:
   - Go to Stash Settings → Metadata Providers → Stash-boxes
   - Add your API endpoints and keys for:
     - StashDB: `https://stashdb.org/graphql`
     - ThePornDB: `https://theporndb.net/graphql` 
     - FansDB: `https://fansdb.cc/graphql`

4. **Enable Plugin**:
   - Go to Stash Settings → Plugins
   - Enable "Performer/Site Sync"

## Configuration

### Plugin Settings
- **Cache Expiration**: How long to cache API responses (1-168 hours, default: 24)
- **Rate Limit**: Delay between API requests (0-10 seconds, default: 2)
- **Source Enables**: Toggle individual sources on/off
- **Source Precedence**: Priority order for merging data (default: StashDB > TPDB > FansDB)
- **Debug Logging**: Enable detailed logging for troubleshooting
- **Name Search**: Allow name-based searches when stash_ids are missing
- **Auto-Create Sites**: Automatically create missing sites/studios when syncing favorites
- **Auto-Create Performers**: Automatically create missing performers when syncing favorites
- **Image Updates**: Allow updating performer images from external sources

### External API Setup
Each external source requires:
1. **Endpoint URL**: The GraphQL endpoint
2. **API Key**: Your personal API key for the service
3. **Display Name**: Friendly name for the source

## Usage

### Basic Operations

1. **Test Your Setup**:
   - Run "Test Connections" to verify all endpoints work
   - Run "Validate Configuration" to check for issues

2. **Update Existing Performers**:
   - "Update All Performers" for bulk updates
   - "Update Single Performer" from performer pages

3. **Import Favorites**:
   - "Sync Favorites from All Sources" to import all
   - Use source-specific sync for targeted imports

### Advanced Features

- **Cache Management**: Clear cache when you want fresh data
- **Sync Reports**: Generate detailed status reports
- **Selective Updates**: Enable/disable sources as needed

## How It Works

### Data Merging
The plugin intelligently merges performer data using configurable source precedence:

1. **Direct Lookup**: If a performer already has a stash_id for a source, fetch data directly
2. **Name Search**: For missing stash_ids, search by performer name for exact matches
3. **Data Merging**: Combine data from all sources using precedence rules
4. **Update Local**: Apply merged data to your local Stash performer

### Cached Performance
- **Smart Caching**: Reduces API calls by caching responses
- **Configurable Expiration**: Control how long cache entries remain valid
- **Automatic Cleanup**: Expired entries are automatically removed

### Error Handling
- **Retry Logic**: Automatic retries with exponential backoff
- **Rate Limiting**: Prevents API rate limit violations
- **Graceful Degradation**: Continues processing even if some sources fail

## Troubleshooting

### Common Issues

1. **No Data Updates**:
   - Check API keys in Stash-boxes configuration
   - Run "Test Connections" to verify connectivity
   - Enable debug logging for detailed error messages

2. **Slow Performance**:
   - Increase cache expiration time
   - Reduce rate limit delay (but watch for rate limiting)
   - Disable unused sources

3. **API Rate Limits**:
   - Increase rate limit delay
   - Reduce concurrent operations
   - Clear cache less frequently

### Debug Information
Enable "Debug Logging" in plugin settings for detailed information about:
- API requests and responses  
- Cache hits/misses
- Data merging decisions
- Error details

## Technical Details

### Dependencies
- **requests**: HTTP client for API communication
- **stashapi-tools**: Stash API integration
- **sqlite3**: Built-in caching database
- **pathlib**: File system operations

### File Structure
- **performer_site_sync.py**: Main plugin logic and task routing
- **performer_site_sync.yml**: Plugin manifest and task definitions  
- **performer_site_sync.js**: UI enhancements and better UX
- **cache/**: SQLite cache database directory (auto-created)

### Supported Data Fields
The plugin can sync these performer attributes:
- Basic info (name, aliases, disambiguation)
- Physical attributes (height, measurements, etc.)
- Career information (start/end years)
- Demographics (ethnicity, country, etc.)
- Images (with precedence-based selection)
- External stash_ids for cross-referencing

## License

This plugin is part of the Stash Community Scripts collection and follows the same licensing terms.

## Support

For issues, feature requests, or contributions:
- [Stash Community Scripts Repository](https://github.com/stashapp/CommunityScripts)
- [Stash Discord Community](https://discord.gg/2TsNFKt)

## Version History

### v1.0.0
- Initial release
- Full sync functionality for StashDB, TPDB, and FansDB
- Manual task controls with enhanced UI
- Intelligent caching and rate limiting
- Comprehensive error handling and reporting
