from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Create FastAPI instance
app = FastAPI(
    title="Demo API",
    description="A simple FastAPI demo with RESTful endpoints",
    version="1.0.0"
)

# Pydantic models for request/response
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None

# In-memory storage (for demo purposes)
items_db = []
next_id = 1

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Demo API!", "version": "1.0.0"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# GET all items
@app.get("/items", response_model=List[Item])
async def get_items():
    """Get all items"""
    return items_db

# GET item by ID
@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """Get a specific item by ID"""
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# POST create new item
@app.post("/items", response_model=Item)
async def create_item(item: Item):
    """Create a new item"""
    global next_id
    item.id = next_id
    next_id += 1
    items_db.append(item)
    return item

# PUT update item
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item_update: ItemUpdate):
    """Update an existing item"""
    for i, item in enumerate(items_db):
        if item.id == item_id:
            # Update only provided fields
            update_data = item_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(item, field, value)
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# DELETE item
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """Delete an item"""
    for i, item in enumerate(items_db):
        if item.id == item_id:
            deleted_item = items_db.pop(i)
            return {"message": f"Item '{deleted_item.name}' deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

# Search items by name
@app.get("/items/search/{name}")
async def search_items(name: str):
    """Search items by name"""
    matching_items = [item for item in items_db if name.lower() in item.name.lower()]
    return matching_items

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
