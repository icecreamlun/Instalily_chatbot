"""
Test module for the search engine implementation.
"""

import logging
from search_engine import SearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_search_repair_info():
    """Test the search_repair_info method."""
    search_engine = SearchEngine()
    
    # Test with a common appliance
    query = "Samsung washing machine not spinning"
    results = search_engine.search_repair_info(query)
    
    logger.info(f"Search results for '{query}':")
    for result in results:
        logger.info(f"Title: {result['title']}")
        logger.info(f"Description: {result['description'][:200]}...")
        logger.info(f"URL: {result['url']}")
        logger.info(f"Source: {result['source']}")
        logger.info("---")

def test_search_repair_stories():
    """Test the search_repair_stories method."""
    search_engine = SearchEngine()
    
    # Test with a common appliance
    query = "LG refrigerator not cooling"
    stories = search_engine.search_repair_stories(query)
    
    logger.info(f"Repair stories for '{query}':")
    for story in stories:
        logger.info(f"Title: {story['title']}")
        logger.info(f"Solution: {story['solution'][:200]}...")
        logger.info(f"Source: {story['source']}")
        logger.info("---")

if __name__ == "__main__":
    logger.info("Testing search_repair_info...")
    test_search_repair_info()
    
    logger.info("\nTesting search_repair_stories...")
    test_search_repair_stories() 