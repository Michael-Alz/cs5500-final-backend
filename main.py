from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ---------------------------------------------------------------------
# Create FastAPI instance
# ---------------------------------------------------------------------
app = FastAPI(
    title="Demo API",
    description="A simple FastAPI demo with RESTful endpoints",
    version="1.0.0",
)

# ---------------------------------------------------------------------
# Pydantic models for request/response
# ---------------------------------------------------------------------


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


# ---------------------------------------------------------------------
# In-memory storage (for demo purposes)
# ---------------------------------------------------------------------
items_db: List[Item] = []
next_id: int = 1

# ---------------------------------------------------------------------
# Root & health endpoints
# ---------------------------------------------------------------------


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {"message": "Welcome to the Demo API!", "version": "1.0.0"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


# ---------------------------------------------------------------------
# CRUD endpoints
# ---------------------------------------------------------------------
@app.get("/items", response_model=List[Item])
async def get_items() -> List[Item]:
    """Get all items"""
    return items_db


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int) -> Item:
    """Get a specific item by ID"""
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.post("/items", response_model=Item)
async def create_item(item: Item) -> Item:
    """Create a new item"""
    global next_id
    item.id = next_id
    next_id += 1
    items_db.append(item)
    return item


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item_update: ItemUpdate) -> Item:
    """Update an existing item"""
    for i, item in enumerate(items_db):
        if item.id == item_id:
            update_data = item_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(item, field, value)
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/items/{item_id}")
async def delete_item(item_id: int) -> dict[str, str]:
    """Delete an item"""
    for i, item in enumerate(items_db):
        if item.id == item_id:
            deleted_item = items_db.pop(i)
            return {"message": f"Item '{deleted_item.name}' deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/items/search/{name}", response_model=List[Item])
async def search_items(name: str) -> List[Item]:
    """Search items by name"""
    return [item for item in items_db if name.lower() in item.name.lower()]


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
