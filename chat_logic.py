import os
from typing import List, Dict, Any, Optional
import requests
from vector_store import VectorStore
from scraper import PartSelectScraper
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

class ChatAgent:
    def __init__(self):
        # Initialize vector store for product information
        self.vector_store = VectorStore()
        
        # Initialize scraper
        self.scraper = PartSelectScraper()
        
        # Get API key from environment variable
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
        
        # API endpoint
        self.api_endpoint = "https://api.deepseek.com/v1/chat/completions"
        
        # System prompt template
        self.system_prompt = """You are a helpful customer service agent for PartSelect.com, specializing in Refrigerator and Dishwasher parts. 
Your primary functions are:
1. Helping customers find the right parts for their appliances
2. Providing installation instructions
3. Troubleshooting common issues
4. Checking part compatibility
5. Assisting with order-related queries

Only answer questions related to refrigerator and dishwasher parts and services. 
For other topics, politely explain that you can only help with refrigerator and dishwasher related queries.

When providing part recommendations or compatibility information, always reference the product database."""

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        # Get relevant product information from vector store
        user_query = messages[-1].content
        relevant_info = await self.vector_store.search_relevant_info(user_query)
        
        # If no relevant info found in database, try to scrape additional information
        if not relevant_info and "part number" in user_query.lower():
            part_number = self._extract_part_number(user_query)
            if part_number:
                product = await self.vector_store.get_product_by_part_number(part_number)
                if product and product.get('product_url'):
                    additional_info = await self.scraper.get_additional_info(product['product_url'])
                    if additional_info:
                        relevant_info = self._format_additional_info(additional_info)
        
        # Prepare messages for API call
        api_messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add context about relevant products if available
        if relevant_info:
            api_messages.append({
                "role": "system",
                "content": f"Relevant product information:\n{relevant_info}"
            })
        
        # Add conversation history
        for message in messages:
            api_messages.append({
                "role": message.role,
                "content": message.content
            })
        
        try:
            # Make API call to Deepseek
            response = requests.post(
                self.api_endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": api_messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the assistant's response
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling Deepseek API: {str(e)}")

    def _extract_part_number(self, query: str) -> Optional[str]:
        """Extract part number from query."""
        # Simple regex to find part numbers like PS12345678
        match = re.search(r'PS\d{8}', query)
        return match.group(0) if match else None

    def _format_additional_info(self, info: Dict) -> str:
        """Format additional information for the prompt."""
        formatted_info = []
        
        if info.get('repair_stories'):
            formatted_info.append("Repair Stories:")
            for story in info['repair_stories']:
                formatted_info.append(f"- {story['title']}")
                formatted_info.append(f"  Symptoms: {story['symptoms']}")
                formatted_info.append(f"  Solution: {story['solution']}")
        
        if info.get('video_url'):
            formatted_info.append(f"\nInstallation Video: {info['video_url']}")
        
        return "\n".join(formatted_info)

    def _format_conversation(self, messages: List[Dict[str, str]]) -> str:
        conversation = self.system_prompt + "\n\n"
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            conversation += f"{role.capitalize()}: {content}\n"
        
        conversation += "Assistant:"
        return conversation

    def _extract_assistant_response(self, full_response: str) -> str:
        # Extract only the last assistant response
        try:
            response_parts = full_response.split("Assistant:")
            return response_parts[-1].strip()
        except:
            return full_response.strip() 