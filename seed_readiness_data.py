from app.core.database import SessionLocal
from app.models.student import Student
import random

db = SessionLocal()

seed_data = [
    # (roll_number, cgpa, easy, medium, hard, profile_completion)
    ("CS21B001", 9.6,  80,  90,  30, 85),
    ("CS21B002", 7.8,  60,  45,  10, 60),
    ("CS21B003", 8.2,  40,  30,   5, 55),
    ("IT21B001", 6.9,  20,  10,   0, 40),
    ("CS22B001", 8.9, 200, 180,  60, 75),
    ("TEST4211", 8.5,  30,  20,   2, 45),
]

for roll, cgpa, easy, med, hard, completion in seed_data:
    s = db.query(Student).filter(Student.roll_number == roll).first()
    if s:
        s.cgpa = cgpa
        s.easy_solved = easy
        s.medium_solved = med
        s.hard_solved = hard
        s.total_problems_solved = easy + med + hard
        s.profile_completion_percent = completion

db.commit()
db.close()
print("Seeded.")
