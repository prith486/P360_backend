import os
import csv
import uuid
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_session_local
from app.models.question import Question
from app.models.enums import DifficultyLevel, QuestionType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FACULTY_ID = "00000000-0000-0000-0000-000000000002"
DATA_DIR = r"C:\Users\PRIHTVIRAJ\Desktop\Placement360_db qsns\leetcode\leetcode-questions-analysis\data\all_questions_data"

def normalize_difficulty(level):
    level = level.strip().lower()
    if level == "easy":
        return DifficultyLevel.EASY
    elif level == "medium":
        return DifficultyLevel.MEDIUM
    elif level == "hard":
        return DifficultyLevel.HARD
    return DifficultyLevel.MEDIUM

def parse_csv_row(row):
    """
    Maps CSV row to Question model fields.
    """
    try:
        title = row.get("Question Title", "").strip()
        slug = row.get("Question Slug", "").strip()
        description = row.get("Question Text", "").strip()
        difficulty = normalize_difficulty(row.get("Difficulty Level", "Medium"))
        
        # Tags
        tags_str = row.get("Topic Tagged text", "")
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        
        # Companies
        companies_str = row.get("company tag", "")
        companies = [c.strip() for c in companies_str.split(",") if c.strip()]
        
        # Hints
        hints_str = row.get("Hints", "")
        hints = [hints_str.strip()] if hints_str.strip() else []
        
        # Statistics
        total_submissions = int(row.get("total submission", 0))
        total_accepted = int(row.get("total accepted", 0))
        
        # Success Rate
        success_rate = 0.0
        try:
            success_rate = float(row.get("Success Rate", 0))
        except:
            pass
            
        return {
            "title": title,
            "slug": slug,
            "description": description,
            "difficulty": difficulty,
            "question_type": QuestionType.CODING,
            "tags": tags,
            "companies": companies,
            "hints": hints,
            "total_submissions": total_submissions,
            "total_accepted": total_accepted,
            "acceptance_rate": success_rate,
            "created_by": FACULTY_ID,
            "is_public": True,
            "is_active": True,
            "max_score": 100, # Default
        }
    except Exception as e:
        logger.error(f"Error parsing row: {e}")
        return None

def import_questions():
    db: Session = get_session_local()()
    
    # Get existing slugs to avoid duplicates
    existing_slugs = {q.slug for q in db.query(Question.slug).all()}
    logger.info(f"Found {len(existing_slugs)} existing questions in DB.")
    
    count = 0
    skipped = 0
    
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    
    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        logger.info(f"Processing {filename}...")
        
        with open(filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data = parse_csv_row(row)
                if not data:
                    continue
                    
                if data["slug"] in existing_slugs:
                    skipped += 1
                    continue
                
                # Double check mandatory fields
                if not data["title"] or not data["slug"] or not data["description"]:
                    skipped += 1
                    continue
                
                # Check description length (min 20 per schema)
                if len(data["description"]) < 20:
                    # Pad description if it's too short but seems valid
                    data["description"] = data["description"].ljust(20, " ")

                question = Question(**data)
                db.add(question)
                existing_slugs.add(data["slug"])
                count += 1
                
                if count % 100 == 0:
                    db.commit()
                    logger.info(f"Progress: {count} questions imported...")

    db.commit()
    db.close()
    logger.info(f"Import complete! Total imported: {count}, Skipped: {skipped}")

if __name__ == "__main__":
    import_questions()
