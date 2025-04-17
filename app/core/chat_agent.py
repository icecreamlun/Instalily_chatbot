from typing import List, Dict
import re
from app.core.vector_store import VectorStore
from app.core.search_engine import SearchEngine
from app.core.repair_chain import RepairChain

class ChatAgent:
    def __init__(self, vector_store, cart_manager, chat_model, logger):
        self.vector_store = vector_store
        self.cart_manager = cart_manager
        self.chat_model = chat_model
        self.logger = logger

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response using the chat model."""
        try:
            # Extract the last user message
            user_message = next((msg for msg in reversed(messages) if msg.get("role") == "user"), None)
            if not user_message:
                return "I didn't receive any message. Please try again."
            
            content = user_message.get("content", "").lower()
            
            # Check for cart operations
            if "add" in content and "cart" in content:
                # Extract part number
                part_number = re.search(r'PS\d{8}', content)
                if part_number:
                    part_number = part_number.group(0)
                    self.logger.info(f"Adding item to cart: {part_number}")
                    
                    # Get product info
                    product = await self.vector_store.get_product_by_part_number(part_number)
                    if product:
                        self.logger.info(f"Found product: {product}")
                        
                        # Add to cart
                        success = self.cart_manager.add_to_cart(
                            part_number=part_number,
                            name=product.get('name', ''),
                            price=float(product.get('price', 0))
                        )
                        
                        if success:
                            self.logger.info("Item added to cart successfully")
                            return f"I've added {product.get('name', '')} to your cart. You can view your cart by asking me to show it."
                        else:
                            self.logger.error("Failed to add item to cart")
                            return "I couldn't add the item to your cart. Please try again."
                    else:
                        self.logger.error(f"Product not found: {part_number}")
                        return f"Product {part_number} not found in our database."
            
            elif "remove" in content and "cart" in content:
                # Extract part number
                part_number = re.search(r'PS\d{8}', content)
                if part_number:
                    part_number = part_number.group(0)
                    self.logger.info(f"Removing item from cart: {part_number}")
                    
                    # Remove from cart
                    success = self.cart_manager.remove_from_cart(part_number)
                    if success:
                        self.logger.info("Item removed from cart successfully")
                        return f"I've removed the item with part number {part_number} from your cart."
                    else:
                        self.logger.error("Failed to remove item from cart")
                        return "I couldn't remove the item from your cart. Please try again."
            
            elif "show" in content and "cart" in content:
                self.logger.info("Getting cart contents")
                # Get cart contents
                items = self.cart_manager.get_cart()
                total = self.cart_manager.get_cart_total()
                
                self.logger.info(f"Cart contents: {items}")
                
                if not items:
                    return "Your cart is empty. You can add items by asking me to add them to your cart."
                
                response = "Here are the items in your cart:\n\n"
                for item in items:
                    response += f"Part Number: {item.part_number}\n"
                    response += f"Name: {item.name}\n"
                    response += f"Price: ${item.price}\n"
                    response += f"Quantity: {item.quantity}\n\n"
                
                response += f"Total: ${total:.2f}\n\n"
                response += "You can remove items by saying 'remove PS12345678'."
                return response
            
            # If no cart operation detected, use the chat model
            return await self.chat_model.generate_response(messages)
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return "I'm sorry, I encountered an error while processing your request. Please try again." 