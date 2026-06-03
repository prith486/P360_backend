import os
import sys

# Add project root to sys path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import get_db

def update_database():
    db = next(get_db())
    
    try:
        print("Updating student row...")
        db.execute(text("""
        UPDATE students SET
          roll_number = 'CS21B001',
          branch = 'computer_science',
          current_year = 'fourth',
          section = 'A',
          cgpa = 8.75,
          total_problems_solved = 284,
          easy_solved = 120,
          medium_solved = 130,
          hard_solved = 34,
          readiness_score = 78.5,
          is_placement_ready = true,
          profile_completion_percent = 78.00,
          skills = '["DSA", "Web Development", "System Design", "Python", "Databases"]',
          preferred_roles = '["Software Engineer", "Backend Developer", "Full Stack Developer"]',
          languages_known = '["Python", "JavaScript", "C++", "Java"]',
          leetcode_username = 'aarav_sharma',
          github_username = 'aaravsharma',
          linkedin_url = 'https://linkedin.com/in/aaravsharma',
          willing_to_relocate = true,
          expected_ctc_min = 600000,
          expected_ctc_max = 1200000
        WHERE id = '521c96ec-9c72-4448-9f37-67c68b29ce9f';
        """))
        
        print("Updating auth.users for student...")
        db.execute(text("""
        UPDATE auth.users SET
          raw_user_meta_data = '{"full_name": "Aarav Sharma", "role": "student"}',
          email = 'aarav@placement360.dev'
        WHERE id = '00000000-0000-0000-0000-000000000001';
        """))
        
        print("Updating faculty row...")
        db.execute(text("""
        UPDATE faculty SET
          employee_id = 'FAC2021001',
          department = 'computer_science',
          designation = 'Associate Professor',
          specialization = 'Data Structures, Algorithms, Placement Training',
          can_create_assessments = true,
          can_view_all_students = true,
          can_grade_submissions = true,
          office_location = 'Block A, Room 203',
          office_hours = 'Mon-Fri, 10AM-12PM'
        WHERE id = '438058a6-4345-4906-8f7e-85023df37d10';
        """))
        
        print("Updating auth.users for faculty...")
        db.execute(text("""
        UPDATE auth.users SET
          raw_user_meta_data = '{"full_name": "Dr. Priya Sharma", "role": "faculty"}',
          email = 'priya@placement360.dev'
        WHERE id = '00000000-0000-0000-0000-000000000002';
        """))
        
        # Commit all transactions 
        db.commit()
        print("Database updated successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error updating database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_database()
