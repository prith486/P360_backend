import uuid
from enum import Enum

class BranchType(Enum):
    COMPUTER_SCIENCE = "computer_science"

class AcademicYear(Enum):
    FOURTH = "fourth"

branch_map = {
    "computer_science": ["CS", "Computer Science", "CSE"]
}

year_map = {
    "fourth": ["Fourth Year", "Final Year", "4th Year"]
}

# Values from Aarav's DB record
branch_val = "computer_science"
year_val = "fourth"
batch_year = 2021

student_branches = [branch_val]
if branch_val in branch_map:
    student_branches.extend(branch_map[branch_val])
    
student_years = [year_val, str(batch_year)]
if year_val in year_map:
    student_years.extend(year_map[year_val])

print(f"Student Branches: {student_branches}")
print(f"Student Years: {student_years}")

# Values from Assessment Record 'stfyghjk...'
target_branches = ['CS', 'Civil', 'Mech']
target_years = ['Final Year', 'Third Year', 'Second Year']

b_match = not target_branches
if target_branches:
    for b in student_branches:
        if b in target_branches:
            b_match = True
            break

y_match = not target_years
if target_years:
    for y in student_years:
        if y in target_years:
            y_match = True
            break

print(f"b_match: {b_match}")
print(f"y_match: {y_match}")
print(f"Overall Match: {b_match and y_match}")
