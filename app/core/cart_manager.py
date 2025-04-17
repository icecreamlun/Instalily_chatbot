"""
This module manages shopping cart operations for refrigerator and dishwasher parts.
"""

from typing import Dict, List, Optional
import logging
from dataclasses import dataclass

@dataclass
class CartItem:
    part_number: str
    name: str
    price: float
    quantity: int

class CartManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cart: List[CartItem] = []  # Single cart for all users
        
    def add_to_cart(self, part_number: str, name: str, price: float, quantity: int = 1) -> bool:
        """
        Add an item to the cart.
        
        Args:
            part_number: Part number of the item
            name: Name of the item
            price: Price of the item
            quantity: Quantity to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Adding item to cart: {part_number}, {name}, {price}, {quantity}")
            
            # Check if item already exists in cart
            for item in self.cart:
                if item.part_number == part_number:
                    self.logger.info(f"Item already in cart, updating quantity: {item.quantity} -> {item.quantity + quantity}")
                    item.quantity += quantity
                    return True
            
            # Add new item
            new_item = CartItem(
                part_number=part_number,
                name=name,
                price=price,
                quantity=quantity
            )
            self.logger.info(f"Adding new item to cart: {new_item}")
            self.cart.append(new_item)
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding to cart: {str(e)}")
            return False
    
    def remove_from_cart(self, part_number: str) -> bool:
        """
        Remove an item from the cart.
        
        Args:
            part_number: Part number of the item to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.cart = [
                item for item in self.cart
                if item.part_number != part_number
            ]
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing from cart: {str(e)}")
            return False
    
    def get_cart(self) -> List[CartItem]:
        """
        Get the cart contents.
        
        Returns:
            List of CartItem objects
        """
        return self.cart
    
    def clear_cart(self) -> bool:
        """
        Clear the cart.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.cart = []
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing cart: {str(e)}")
            return False
    
    def get_cart_total(self) -> float:
        """
        Calculate the total price of items in the cart.
        
        Returns:
            float: Total price
        """
        return sum(item.price * item.quantity for item in self.cart) 