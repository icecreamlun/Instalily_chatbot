"""
This module implements search functionality using Bing Web Search API.
It provides a way to search for repair information and related content.
"""

import requests
from typing import Dict, List, Optional
import logging
from urllib.parse import quote_plus
import time
import random
import os
from app.core.vector_store import VectorStore

class SearchEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"
        self.subscription_key = os.getenv('BING_SEARCH_KEY')
        if not self.subscription_key:
            raise ValueError("BING_SEARCH_KEY environment variable is not set")
            
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search_repair_info(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for repair information using Bing Web Search API.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries containing search results
        """
        try:
            # Add repair-related keywords to improve search results
            enhanced_query = f"{query} repair guide fix solution"
            
            # Construct the search URL
            search_url = f"{self.base_url}?q={quote_plus(enhanced_query)}&count={max_results}&responseFilter=Webpages"
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 2))
            
            # Make the request
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            results = []
            
            # Extract web search results
            for item in data.get('webPages', {}).get('value', [])[:max_results]:
                results.append({
                    'title': item.get('name', ''),
                    'description': item.get('snippet', ''),
                    'url': item.get('url', ''),
                    'source': 'Bing Web Search'
                })
            
            self.logger.info(f"Found {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching for repair info: {str(e)}")
            return []

    def search_repair_stories(self, query: str) -> List[Dict]:
        """
        Search specifically for repair stories and experiences.
        
        Args:
            query: The search query
            
        Returns:
            List of dictionaries containing repair stories
        """
        try:
            # Add keywords to find repair stories
            enhanced_query = f"{query} repair story experience fix solution forum"
            
            # Construct the search URL
            search_url = f"{self.base_url}?q={quote_plus(enhanced_query)}&count=10&responseFilter=Webpages"
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 2))
            
            # Make the request
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            stories = []
            
            # Extract web search results
            for item in data.get('webPages', {}).get('value', []):
                # Filter for forum posts and repair stories
                if any(keyword in item.get('url', '').lower() for keyword in ['forum', 'community', 'discussion']):
                    stories.append({
                        'title': item.get('name', ''),
                        'solution': item.get('snippet', ''),
                        'success': True,
                        'source': 'Bing Web Search'
                    })
            
            self.logger.info(f"Found {len(stories)} repair stories for query: {query}")
            return stories
            
        except Exception as e:
            self.logger.error(f"Error searching for repair stories: {str(e)}")
            return [] 