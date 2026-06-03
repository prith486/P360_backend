from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseService(Generic[ModelType]):
    """
    Base service class with common CRUD operations.
    
    All service classes should inherit from this to get standard methods.
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get single record by ID."""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: dict) -> ModelType:
        """Create new record."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_in: dict
    ) -> ModelType:
        """Update existing record."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Delete record by ID."""
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
