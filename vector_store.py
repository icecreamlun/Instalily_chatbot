import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import json
import os

class VectorStore:
    def __init__(self):
        # Initialize the sentence transformer model
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize FAISS index
        self.dimension = 384  # Dimension of the sentence transformer embeddings
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Store for product information
        self.products: List[Dict] = []
        
        # Create part number index
        self.part_number_index: Dict[str, Dict] = {}
        
        # Load product data
        self._load_product_data()
        
    def _load_product_data(self):
        """Load product data from JSON file and create embeddings."""
        try:
            with open('product_data.json', 'r') as f:
                data = json.load(f)
                self.products = data.get('products', [])
                
            # Create part number index
            for product in self.products:
                if 'part_number' in product:
                    self.part_number_index[product['part_number']] = product
                
            # Create embeddings for all products
            texts = [self._create_product_text(product) for product in self.products]
            embeddings = self.encoder.encode(texts)
            
            # Add to FAISS index
            self.index.add(np.array(embeddings).astype('float32'))
            
        except FileNotFoundError:
            print("Product data file not found. Vector store initialized empty.")
        except json.JSONDecodeError:
            print("Error decoding product data file. Vector store initialized empty.")
    
    def _create_product_text(self, product: Dict) -> str:
        """Create a searchable text representation of a product."""
        return f"{product.get('name', '')} {product.get('description', '')} {product.get('model_compatibility', '')} {product.get('part_number', '')}"
    
    async def search_relevant_info(self, query: str, k: int = 3) -> Optional[str]:
        """Search for relevant product information based on the query."""
        if not self.products:
            return None
            
        # Encode the query
        query_vector = self.encoder.encode([query])
        
        # Search in FAISS
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), k)
        
        # Format results
        results = []
        for idx in indices[0]:
            if idx < len(self.products):
                product = self.products[idx]
                results.append(
                    f"Part Number: {product.get('part_number', 'N/A')}\n"
                    f"Name: {product.get('name', 'N/A')}\n"
                    f"Compatible Models: {product.get('model_compatibility', 'N/A')}\n"
                    f"Installation Guide: {product.get('installation_guide', 'N/A')}\n"
                    f"Product URL: {product.get('product_url', 'N/A')}\n"
                    f"Installation Video: {product.get('part_video', 'N/A')}\n"
                )
                
                # Add repair stories if available
                if product.get('repair_stories'):
                    results.append("Repair Stories:")
                    for story in product['repair_stories']:
                        results.append(f"- {story['title']}")
                        results.append(f"  Symptoms: {story['symptoms']}")
                        results.append(f"  Solution: {story['solution']}")
        
        return "\n".join(results) if results else None
    
    async def get_product_by_part_number(self, part_number: str) -> Optional[Dict]:
        """Get product information by part number."""
        return self.part_number_index.get(part_number)
    
    async def add_product(self, product: Dict):
        """Add a new product to the vector store."""
        self.products.append(product)
        
        # Update part number index
        if 'part_number' in product:
            self.part_number_index[product['part_number']] = product
        
        # Create and add embedding
        text = self._create_product_text(product)
        embedding = self.encoder.encode([text])
        self.index.add(np.array(embedding).astype('float32'))
    
    def save_products(self):
        """Save product data to file."""
        with open('product_data.json', 'w') as f:
            json.dump({"products": self.products}, f) 