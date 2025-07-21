#!/usr/bin/env python3
"""
Test script to verify authentication fixes
This should be run through Stash to test the server_connection approach
"""

import json
import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

import stashapi.log as log
from modules.config import ConfigManager
from modules.graphql_client import GraphQLClient

def main():
    try:
        # Read JSON input from stdin (simulating Stash plugin input)
        json_input = json.loads(sys.stdin.read())
        
        log.info("Starting authentication test")
        log.debug(f"JSON input keys: {list(json_input.keys())}")
        
        # Initialize ConfigManager with server_connection
        server_connection = json_input.get("server_connection")
        if server_connection:
            log.info("Found server_connection in JSON input")
            log.debug(f"Server connection keys: {list(server_connection.keys())}")
        else:
            log.warning("No server_connection found in JSON input")
        
        # Initialize ConfigManager
        config_manager = ConfigManager(server_connection)
        log.info("ConfigManager initialized successfully")
        
        # Test basic Stash connection
        try:
            performers = config_manager.stash.find_performers({"per_page": 1})
            if performers:
                log.info(f"✅ Authentication SUCCESS: Retrieved {len(performers)} performers from Stash")
                print(json.dumps({"status": "success", "message": "Authentication working correctly"}))
            else:
                log.warning("⚠️  Authentication might be working but no performers found")
                print(json.dumps({"status": "warning", "message": "No performers found but no auth error"}))
        except Exception as e:
            log.error(f"❌ Authentication FAILED: {str(e)}")
            print(json.dumps({"status": "error", "message": f"Authentication failed: {str(e)}"}))
            
    except Exception as e:
        log.error(f"❌ Test script failed: {str(e)}")
        print(json.dumps({"status": "error", "message": f"Test failed: {str(e)}"}))

if __name__ == "__main__":
    main()
