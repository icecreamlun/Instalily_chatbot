import logging
from scraper import PartSelectScraper

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Change to DEBUG level
logger = logging.getLogger(__name__)

def test_scraper():
    test_url = "https://www.partselect.com/PS11752778-Whirlpool-WPW10321304-Refrigerator-Door-Shelf-Bin.htm"
    
    with PartSelectScraper() as scraper:
        # Test get_product_page
        logger.info("Testing get_product_page...")
        html_content = scraper.get_product_page(test_url)
        if html_content:
            logger.info("Successfully fetched product page")
            # Log a sample of the HTML content
            logger.debug(f"HTML content sample: {html_content[:1000]}...")
        else:
            logger.error("Failed to fetch product page")
            return

        # Test extract_repair_stories
        logger.info("\nTesting extract_repair_stories...")
        stories = scraper.extract_repair_stories(html_content)
        logger.info(f"Found {len(stories)} repair stories")
        for i, story in enumerate(stories, 1):
            logger.info(f"\nStory {i}:")
            logger.info(f"Title: {story['title']}")
            logger.info(f"Solution: {story['solution']}")
            if 'parts_used' in story:
                logger.info(f"Parts Used: {', '.join(story['parts_used'])}")

        # Test get_additional_info
        logger.info("\nTesting get_additional_info...")
        additional_info = scraper.get_additional_info(test_url)
        logger.info(f"Found {len(additional_info['repair_stories'])} repair stories")

if __name__ == "__main__":
    test_scraper() 