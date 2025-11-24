from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List
import os
import uvicorn

app = FastAPI(title="Product Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory product storage (for demo purposes)
products: Dict[int, dict] = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10},
    2: {"id": 2, "name": "Mouse", "price": 29.99, "stock": 50},
    3: {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 30}
}

# Pydantic models
class StockUpdate(BaseModel):
    quantity: int

class Product(BaseModel):
    id: int
    name: str
    price: float
    stock: int

class StockResponse(BaseModel):
    product_id: int
    stock: int

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "product-service"}

@app.get("/products", response_model=List[Product])
async def get_products():
    """Get all products"""
    return list(products.values())

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int = Path(..., gt=0)):
    """Get a specific product by ID"""
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    return products[product_id]

@app.get("/products/{product_id}/stock", response_model=StockResponse)
async def get_stock(product_id: int = Path(..., gt=0)):
    """Get stock level for a product"""
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product_id": product_id, "stock": products[product_id]["stock"]}

@app.put("/products/{product_id}/stock", response_model=StockResponse)
async def update_stock(
    stock_update: StockUpdate,
    product_id: int = Path(..., gt=0)
):
    """Update stock level (used by order-service)"""
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    quantity = stock_update.quantity
    new_stock = products[product_id]["stock"] + quantity
    
    if new_stock < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    products[product_id]["stock"] = new_stock
    return {"product_id": product_id, "stock": new_stock}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    uvicorn.run(app, host='0.0.0.0', port=port)
