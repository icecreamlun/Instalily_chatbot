# PartSelect Chatbot - Intelligent Appliance Parts Assistant

## Overview
The PartSelect Chatbot is an intelligent assistant designed to help customers with refrigerator and dishwasher parts. It provides product information, installation guidance, troubleshooting assistance, and shopping support through natural language interactions.

## Key Features

### 1. Intelligent Product Search
- Vector-based semantic search using FAISS
- Product compatibility checking
- Detailed product information retrieval
- Installation guides and videos

### 2. Advanced Repair Diagnosis
- Chain of Thought (CoT) based fault analysis
- Multi-step diagnostic process
- Safety considerations and preventive measures
- Repair stories and solutions

### 3. Shopping Experience
- Shopping cart management
- Product comparison
- Price information
- Order assistance

### 4. Natural Language Understanding
- Context-aware responses
- Multi-turn conversations
- Domain-specific knowledge
- Error handling and fallback responses

## System Architecture

### Backend Components

1. **Chat Agent**
   - Handles user interactions
   - Manages conversation flow
   - Integrates with Deepseek LLM
   - Coordinates between different components

2. **Vector Store**
   - Product information storage
   - Semantic search capabilities
   - FAISS-based similarity search
   - Product embeddings management

3. **Repair Chain**
   - Fault diagnosis system
   - Chain of Thought reasoning
   - Problem categorization
   - Solution generation

4. **Search Engine**
   - Bing Web Search integration
   - Repair information retrieval
   - Product data enrichment
   - External knowledge integration

5. **Cart Manager**
   - Shopping cart operations
   - Order management
   - Price calculations
   - Inventory tracking

### Data Flow

1. **User Query Processing**
   ```
   User Query → Chat Agent → Vector Store/Search Engine → Response Generation
   ```

2. **Repair Diagnosis**
   ```
   Problem Description → Repair Chain → Diagnosis Steps → Solution Generation
   ```

3. **Shopping Experience**
   ```
   Product Query → Vector Store → Cart Manager → Order Processing
   ```

## Technical Implementation

### Core Technologies
- FastAPI for backend services
- FAISS for vector similarity search
- Sentence Transformers for text embeddings
- Deepseek LLM for natural language understanding
- Bing Web Search API for external information

### Data Structures

1. **Product Information**
   ```json
   {
     "part_number": "PS11752778",
     "name": "Refrigerator Door Shelf Bin",
     "description": "...",
     "model_compatibility": "WDT780SAEM1, WRF535SMHZ",
     "installation_guide": "...",
     "price": 36.08,
     "product_url": "...",
     "part_video": "...",
     "repair_stories": [...]
   }
   ```

2. **Diagnosis Steps**
   ```python
   @dataclass
   class DiagnosisStep:
       step_number: int
       description: str
       possible_causes: List[str]
       verification_method: str
       solution: str
       safety_notes: Optional[str]
   ```

### API Endpoints

1. **Chat Endpoint**
   ```
   POST /api/chat
   Request: { messages: [{ role: str, content: str }] }
   Response: { message: { role: str, content: str } }
   ```

2. **Cart Endpoint**
   ```
   GET /api/cart
   Response: { items: List[Dict], total: float }
   ```

## Example Interactions

### 1. Product Information
```
User: Can you show me some refrigerator items?
Bot: Here are some refrigerator parts available:
    1. Refrigerator Door Shelf Bin (PS11752778) - $36.08
    2. Refrigerator Water Filter (PS11746285) - $49.99
```

### 2. Installation Guidance
```
User: How do I install the refrigerator door shelf bin?
Bot: Here's the installation guide:
    1. Turn off water supply
    2. Unplug refrigerator
    3. Remove old ice shelf
    4. Connect water line to new ice shelf
    5. Secure mounting bracket
    6. Plug in and test
```

### 3. Repair Diagnosis
```
User: My refrigerator is not cooling properly. What could be wrong?
Bot: Let me analyze the problem:
    1. Problem Type: Mechanical
    2. Initial Assessment:
       - Appliance: Refrigerator
       - Problem: Not cooling
       - Complexity: Medium
    3. Diagnosis Steps:
       - Check power supply
       - Inspect cooling system
       - Verify temperature control
```

### 4. Shopping Experience
```
User: Add the refrigerator door shelf bin to my cart
Bot: I've added the Refrigerator Door Shelf Bin (PS11752778) to your cart.
     Price: $36.08
     You can view your cart by saying 'show my cart'.
```

## System Design Highlights

### 1. Modular Architecture
- Independent components for different functionalities
- Easy to extend and maintain
- Clear separation of concerns

### 2. Intelligent Search
- Vector-based semantic search
- Context-aware results
- Product compatibility checking

### 3. Advanced Diagnosis
- Chain of Thought reasoning
- Multi-step problem analysis
- Safety considerations
- Preventive measures

### 4. Scalable Design
- Vector store for efficient search
- API-based architecture
- Easy integration with external services

## Future Enhancements

1. **Enhanced Product Search**
   - Image-based search
   - Voice search capabilities
   - Advanced filtering options

2. **Improved Diagnosis**
   - Machine learning-based fault prediction
   - Real-time monitoring integration
   - Automated part recommendations

3. **Extended Shopping Features**
   - Payment integration
   - Order tracking
   - Personalized recommendations

4. **Advanced User Experience**
   - Multi-language support
   - Voice interaction
   - Mobile app integration

## Conclusion
The PartSelect Chatbot demonstrates how AI and natural language processing can enhance the customer experience in the appliance parts industry. Its combination of intelligent search, advanced diagnosis, and seamless shopping experience provides a comprehensive solution for customers' needs. 