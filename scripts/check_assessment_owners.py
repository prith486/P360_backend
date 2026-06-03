import os
import uuid
from sqlalchemy import create_session, create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# We need to find the models
import sys
sys.path.append(r'c:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend')

from app.models.assessment import Assessment
from app.models.auth_user import AuthUser
from app.core.database import SessionLocal

db = SessionLocal()

print("Listing all assessments and their creators:")
assessments = db.query(Assessment).all()
for a in assessments:
    creator = db.query(AuthUser).filter(AuthUser.id == a.created_by).first()
    creator_name = creator.full_name if creator else "Unknown"
    print(f"ID: {a.id} | Title: {a.title} | Creator ID: {a.created_by} | Creator Name: {creator_name} | Status: {a.status} | Published: {a.is_published}")

db.close()
