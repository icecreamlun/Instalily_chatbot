"""
This module contains a backup implementation of web scraping functionality using Selenium.
This implementation is kept for reference but is not the primary strategy for data collection.

Note: This implementation is not actively used in production.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
import asyncio
from aiohttp import ClientSession, TCPConnector
import logging
import random
import time
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from app.core.vector_store import VectorStore

class PartSelectScraper:
    def __init__(self):
        self.base_url = "https://www.partselect.com"
        self.logger = logging.getLogger(__name__)
        
        # Initialize Selenium options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')  # Run in headless mode
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Initialize driver
        self.driver = None

    def __enter__(self):
        # Get the ChromeDriver path
        driver_path = ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
        
        # Find the actual chromedriver executable
        driver_dir = os.path.dirname(driver_path)
        for root, dirs, files in os.walk(driver_dir):
            for file in files:
                if file == 'chromedriver':
                    driver_path = os.path.join(root, file)
                    break
        
        # Make sure the chromedriver is executable
        os.chmod(driver_path, 0o755)
        
        service = Service(executable_path=driver_path)
        self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()

    def get_product_page(self, product_url: str) -> Optional[str]:
        """Fetch product page content using Selenium."""
        try:
            self.driver.get(product_url)
            
            # Wait for page to load with a longer timeout
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for page to be fully loaded with a longer delay
            time.sleep(5)
            
            # Log the page source for debugging
            self.logger.debug("Page source after initial load:")
            self.logger.debug(self.driver.page_source[:1000])
            
            # Try to find any repair-related content with multiple attempts
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # First try to find repair stories section
                    repair_section = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='repair']"))
                    )
                    self.logger.debug(f"Found repair section on attempt {attempt + 1}")
                    break
                except Exception as e:
                    if attempt < max_attempts - 1:
                        self.logger.debug(f"Attempt {attempt + 1} failed, trying to scroll and wait")
                        # Scroll to bottom to trigger loading
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(3)
                    else:
                        self.logger.warning("Could not find repair section after all attempts")
            
            # Get the final page source
            page_source = self.driver.page_source
            self.logger.debug(f"Final page source length: {len(page_source)}")
            
            return page_source
        except Exception as e:
            self.logger.error(f"Error fetching product page with Selenium: {str(e)}")
            return None

    def extract_repair_stories(self, html_content: str) -> List[Dict]:
        """Extract repair stories from product page."""
        stories = []
        if not html_content:
            return stories
            
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try different selectors to find repair stories
            selectors = [
                'div[class*="repair"]',
                'div[class*="story"]',
                'div[class*="fix"]',
                'div[class*="solution"]'
            ]
            
            for selector in selectors:
                repair_stories = soup.select(selector)
                if repair_stories:
                    self.logger.debug(f"Found {len(repair_stories)} stories using selector: {selector}")
                    break
            
            for story in repair_stories:
                try:
                    # Get title - try different possible selectors
                    title = story.find(['h2', 'h3', 'h4', 'div'], {'class': lambda x: x and ('title' in x.lower() or 'heading' in x.lower())})
                    
                    # Get instruction - try different possible selectors
                    instruction = story.find(['div', 'p'], {'class': lambda x: x and ('instruction' in x.lower() or 'content' in x.lower() or 'text' in x.lower())})
                    
                    # Get parts used - try different possible selectors
                    parts = story.find(['div', 'ul'], {'class': lambda x: x and ('part' in x.lower() or 'component' in x.lower())})
                    
                    if title or instruction:
                        story_data = {
                            "title": title.get_text(strip=True) if title else "Repair Story",
                            "symptoms": "",  # Not needed as per user request
                            "solution": instruction.get_text(strip=True) if instruction else "",
                            "success": True
                        }
                        
                        # Add parts used if available
                        if parts:
                            parts_list = []
                            for part in parts.find_all(['a', 'li', 'span']):
                                part_name = part.get_text(strip=True)
                                if part_name:
                                    parts_list.append(part_name)
                            if parts_list:
                                story_data["parts_used"] = parts_list
                        
                        stories.append(story_data)
                        self.logger.debug(f"Extracted story: {story_data['title']}")
                except Exception as e:
                    self.logger.warning(f"Error extracting individual story: {str(e)}")
                    continue
            
            if not stories:
                self.logger.warning("No repair stories found in the page")
                
        except Exception as e:
            self.logger.error(f"Error extracting repair stories: {str(e)}")
        
        return stories

    def extract_video_url(self, html_content: str) -> Optional[str]:
        """Extract video URL from product page."""
        if not html_content:
            return None
            
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # First try to find video in the repair video section
            video_section = soup.find('div', {'id': 'repair-video'}) or \
                          soup.find('div', {'class': 'repair-video'}) or \
                          soup.find('div', {'class': 'video-container'})
            
            if video_section:
                # Try to find iframe with video
                iframe = video_section.find('iframe', {'src': lambda x: x and ('youtube.com' in x or 'vimeo.com' in x)})
                if iframe and iframe.get('src'):
                    return iframe['src']
                
                # Try to find video element
                video = video_section.find('video', {'src': True})
                if video and video.get('src'):
                    return video['src']
                
                # Try to find video source element
                source = video_section.find('source', {'src': True})
                if source and source.get('src'):
                    return source['src']
            
            # If no video found in repair video section, try searching the entire page
            # Look for any iframe with video URL
            iframe = soup.find('iframe', {'src': lambda x: x and ('youtube.com' in x or 'vimeo.com' in x)})
            if iframe and iframe.get('src'):
                return iframe['src']
            
            # Look for any video element
            video = soup.find('video', {'src': True})
            if video and video.get('src'):
                return video['src']
            
            # Look for any video source element
            source = soup.find('source', {'src': True})
            if source and source.get('src'):
                return source['src']
            
            self.logger.warning("No video URL found on the page")
            
        except Exception as e:
            self.logger.error(f"Error extracting video URL: {str(e)}")
            
        return None

    def get_additional_info(self, product_url: str) -> Dict:
        """Get repair stories and Q&A from the website."""
        html_content = self.get_product_page(product_url)
        if not html_content:
            return {"repair_stories": []}

        return {
            "repair_stories": self.extract_repair_stories(html_content)
        }

    def search_repair_stories(self, query: str) -> List[Dict]:
        """Search for repair stories matching the query."""
        try:
            search_url = f"{self.base_url}/Search.aspx?SearchTerm={query}"
            html_content = self.get_product_page(search_url)
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                # Extract relevant stories from search results
                # Implementation depends on the actual search results page structure
                return []
        except Exception as e:
            self.logger.error(f"Error searching repair stories: {str(e)}")
        return [] 