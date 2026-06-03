"""
Test CRUD endpoints for database verification.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import get_db
from app.models.test import TestItem

router = APIRouter()

# Pydantic schemas
class TestItemCreate(BaseModel):
    name: str 
    description: Optional[str] = None
    is_active: bool = True

class TestItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True

@router.post("/", response_model=TestItemResponse, status_code=status.HTTP_201_CREATED)
async def create_test_item(item: TestItemCreate, db: Session = Depends(get_db)):
    """Create a new test item."""
    db_item = TestItem(
        name=item.name, 
        description=item.description, 
        is_active=item.is_active
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/", response_model=List[TestItemResponse])
async def list_test_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List all test items."""
    return db.query(TestItem).offset(skip).limit(limit).all()

@router.get("/{item_id}", response_model=TestItemResponse)
async def get_test_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific test item."""
    item = db.query(TestItem).filter(TestItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.delete("/{item_id}")
async def delete_test_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a test item."""
    item = db.query(TestItem).filter(TestItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}
