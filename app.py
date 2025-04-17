from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict
import uvicorn
from chat_logic import ChatAgent
from cart_manager import CartManager, CartItem
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

app = FastAPI(title="PartSelect Chat API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chat agent and cart manager
chat_agent = ChatAgent()
cart_manager = CartManager()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    messages: List[Message]
    model_name: Optional[str] = "deepseek"
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: Message

class CartResponse(BaseModel):
    items: List[Dict]
    total: float

@app.get("/")
async def root():
    return {
        "message": "Welcome to PartSelect Chat API",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Extract the last user message
        user_message = next((msg for msg in reversed(request.messages) if msg.role == "user"), None)
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found in the conversation")
        
        content = user_message.content.lower()
        
        # Create system message
        system_message = Message(
            role="system",
            content="""You are a helpful assistant for PartSelect.com. You can help with:
1. Adding items to cart: When user wants to add an item, use the add_to_cart function with the part number
2. Removing items from cart: When user wants to remove an item, use the remove_from_cart function
3. Viewing cart: When user wants to see their cart, use the get_cart function
4. Repair assistance: For repair questions, use the repair_chain
5. Product search: For product queries, use the vector_store

Available functions:
- add_to_cart(part_number, name, price)
- remove_from_cart(part_number)
- get_cart()
- get_cart_total()

Always respond naturally in conversation, but make sure to use these functions when appropriate."""
        )
        
        # Combine system message with request messages
        messages = [system_message] + request.messages
        
        # Use the chat agent for response
        response = await chat_agent.generate_response(messages)
        return ChatResponse(message=Message(role="assistant", content=response))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def handle_cart_operation(user_id: str, content: str) -> ChatResponse:
    """Handle cart-related operations."""
    if not user_id:
        return ChatResponse(message=Message(
            role="assistant",
            content="Please provide a user_id for cart operations."
        ))
    
    # Extract part number
    part_number = re.search(r'PS\d{8}', content)
    if not part_number:
        return ChatResponse(message=Message(
            role="assistant",
            content="Please provide a valid part number (e.g., PS12345678)."
        ))
    
    part_number = part_number.group(0)
    
    # Get product info from database
    product = await chat_agent.vector_store.get_product_by_part_number(part_number)
    if not product:
        return ChatResponse(message=Message(
            role="assistant",
            content=f"Product {part_number} not found in our database."
        ))
    
    if "add" in content.lower():
        success = cart_manager.add_to_cart(
            user_id=user_id,
            part_number=part_number,
            name=product.get('name', ''),
            price=float(product.get('price', 0))
        )
        
        if success:
            return ChatResponse(message=Message(
                role="assistant",
                content=f"Added {product.get('name', '')} to your cart. You can view your cart by saying 'show my cart' or remove items by saying 'remove {part_number}'."
            ))
        else:
            return ChatResponse(message=Message(
                role="assistant",
                content="Failed to add item to cart. Please try again."
            ))
    
    elif "remove" in content.lower():
        success = cart_manager.remove_from_cart(user_id, part_number)
        if success:
            return ChatResponse(message=Message(
                role="assistant",
                content=f"Removed {product.get('name', '')} from your cart."
            ))
        else:
            return ChatResponse(message=Message(
                role="assistant",
                content="Failed to remove item from cart. Please try again."
            ))
    
    return ChatResponse(message=Message(
        role="assistant",
        content="Please specify whether you want to add or remove an item from your cart."
    ))

async def handle_repair_query(content: str) -> ChatResponse:
    """Handle repair-related queries."""
    from repair_chain import RepairChain
    repair_chain = RepairChain()
    
    # Extract appliance type
    appliance_type = "refrigerator" if "refrigerator" in content else "dishwasher"
    
    # Get repair diagnosis
    diagnosis = repair_chain.diagnose(
        appliance_type=appliance_type,
        problem_description=content
    )
    
    if "error" in diagnosis:
        return ChatResponse(message=Message(
            role="assistant",
            content=diagnosis["message"]
        ))
    
    # Format the diagnosis response
    response_content = _format_diagnosis_response(diagnosis)
    return ChatResponse(message=Message(
        role="assistant",
        content=response_content
    ))

async def handle_shopping_query(user_id: str, content: str) -> ChatResponse:
    """Handle shopping-related queries."""
    # Check for cart operations
    if "show my cart" in content.lower() or "view my cart" in content.lower():
        items = cart_manager.get_cart(user_id)
        total = cart_manager.get_cart_total(user_id)
        
        if not items:
            return ChatResponse(message=Message(
                role="assistant",
                content="Your cart is empty. You can add items by saying 'add PS12345678'."
            ))
        
        response = "Here are the items in your cart:\n\n"
        for item in items:
            response += f"Part Number: {item.part_number}\n"
            response += f"Name: {item.name}\n"
            response += f"Price: ${item.price}\n"
            response += f"Quantity: {item.quantity}\n\n"
        
        response += f"Total: ${total:.2f}\n\n"
        response += "You can remove items by saying 'remove PS12345678'."
        
        return ChatResponse(message=Message(
            role="assistant",
            content=response
        ))
    
    # Check if the query is about refrigerators or dishwashers
    if "refrigerator" not in content and "dishwasher" not in content:
        return ChatResponse(message=Message(
            role="assistant",
            content="I can only help with refrigerator and dishwasher parts. Please specify which type of appliance you're looking for."
        ))
    
    # Search for relevant products
    products = await chat_agent.vector_store.search_relevant_info(content)
    if not products:
        return ChatResponse(message=Message(
            role="assistant",
            content="No matching products found. Please try a different search term."
        ))
    
    # Format product suggestions
    response = "Here are some products that might interest you:\n\n"
    for product in products[:5]:  # Show top 5 results
        response += f"Part Number: {product.get('part_number', 'N/A')}\n"
        response += f"Name: {product.get('name', 'N/A')}\n"
        response += f"Price: ${product.get('price', 'N/A')}\n"
        response += f"Description: {product.get('description', 'N/A')}\n\n"
    
    response += "You can add any of these items to your cart by saying 'add PS12345678' (replace with the actual part number)."
    
    return ChatResponse(message=Message(
        role="assistant",
        content=response
    ))

def _format_diagnosis_response(diagnosis: dict) -> str:
    """Format the diagnosis result into a readable response."""
    response_parts = []
    
    # Add problem type
    response_parts.append(f"Problem Type: {diagnosis['problem_type']}")
    
    # Add initial assessment
    response_parts.append("\nInitial Assessment:")
    for key, value in diagnosis['initial_assessment'].items():
        response_parts.append(f"{key}: {value}")
    
    # Add diagnosis steps
    response_parts.append("\nDiagnosis Steps:")
    for step in diagnosis['diagnosis_steps']:
        response_parts.append(f"\nStep {step['step_number']}: {step['description']}")
        response_parts.append(f"Possible Causes: {', '.join(step['possible_causes'])}")
        response_parts.append(f"Solution: {step['solution']}")
        if step['safety_notes']:
            response_parts.append(f"Safety Notes: {step['safety_notes']}")
    
    # Add preventive measures
    response_parts.append("\nPreventive Measures:")
    for measure in diagnosis['preventive_measures']:
        response_parts.append(f"- {measure}")
    
    # Add safety notes
    response_parts.append("\nSafety Notes:")
    for note in diagnosis['safety_notes']:
        response_parts.append(f"- {note}")
    
    return "\n".join(response_parts)

@app.get("/api/cart/{user_id}", response_model=CartResponse)
async def get_cart(user_id: str):
    """Get the user's cart contents."""
    items = cart_manager.get_cart(user_id)
    total = cart_manager.get_cart_total(user_id)
    
    return CartResponse(
        items=[{
            "part_number": item.part_number,
            "name": item.name,
            "price": item.price,
            "quantity": item.quantity
        } for item in items],
        total=total
    )

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 