from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import httpx
import uvicorn

app = FastAPI(title="Order Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Product service URL (will be injected via environment variable in K8s)
PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://localhost:5001')

# In-memory order storage (for demo purposes)
orders: Dict[int, dict] = {}
order_counter = 1

# Pydantic models
class OrderItem(BaseModel):
    product_id: int
    quantity: int = 1

class CreateOrderRequest(BaseModel):
    items: List[OrderItem]

class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float
    subtotal: float

class Order(BaseModel):
    id: int
    items: List[OrderItemResponse]
    total: float
    status: str

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "order-service"}

@app.get("/orders", response_model=List[Order])
async def get_orders():
    """Get all orders"""
    return list(orders.values())

@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int = Path(..., gt=0)):
    """Get a specific order by ID"""
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders[order_id]

@app.post("/orders", response_model=Order, status_code=201)
async def create_order(order_request: CreateOrderRequest):
    """Create a new order"""
    global order_counter
    
    order_items = []
    total = 0.0
    
    # Validate products and calculate total
    async with httpx.AsyncClient() as client:
        for item in order_request.items:
            product_id = item.product_id
            quantity = item.quantity
            
            # Call product-service to get product details
            try:
                product_response = await client.get(
                    f"{PRODUCT_SERVICE_URL}/products/{product_id}"
                )
                
                if product_response.status_code != 200:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Product {product_id} not found"
                    )
                
                product = product_response.json()
                
                # Check stock availability
                if product['stock'] < quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for product {product_id}"
                    )
                
                # Reserve stock by updating product-service
                stock_response = await client.put(
                    f"{PRODUCT_SERVICE_URL}/products/{product_id}/stock",
                    json={"quantity": -quantity}
                )
                
                if stock_response.status_code != 200:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to reserve stock"
                    )
                
                item_total = product['price'] * quantity
                order_items.append({
                    "product_id": product_id,
                    "product_name": product['name'],
                    "quantity": quantity,
                    "price": product['price'],
                    "subtotal": item_total
                })
                total += item_total
                
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to communicate with product-service: {str(e)}"
                )
    
    # Create order
    order = {
        "id": order_counter,
        "items": order_items,
        "total": total,
        "status": "created"
    }
    
    orders[order_counter] = order
    order_counter += 1
    
    return order

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    uvicorn.run(app, host='0.0.0.0', port=port)
