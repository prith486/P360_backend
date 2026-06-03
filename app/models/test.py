"""
Test model for database verification.
Can be deleted after confirming database works.
"""
from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel

class TestItem(BaseModel):
    """Simple test model to verify database operations."""
    __tablename__ = "test_items"
    
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<TestItem(id={self.id}, name='{self.name}')>"
