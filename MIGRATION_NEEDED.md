# Database Schema Migration Required

## Current Situation

### Problem
The SQLAlchemy models have been updated to use UUID primary keys and custom column names, but the database still has the old schema with:
- Supabase Auth integration (`auth.users` table)
- Different column names (e.g., `encrypted_password` vs `hashed_password`, `phone` vs `phone_number`)
- Potentially different ID types

### Impact
- All authenticated API requests return 500 Internal Server Error
- Token generation works, but user lookup fails due to schema mismatch
- The application cannot function until this is resolved

## Database Schema Inspection Results

### `auth.users` table columns (Supabase Auth):
- id (UUID)
- role
- email
- encrypted_password
- full_name
- phone
- confirmation_token
- recovery_token
- reauthentication_token
- email_change_token_new
- email_change
- phone_change
- phone_change_token
- hashed_password
- email_change_token_current

### `students` table columns:
- id (UUID)
- user_id (UUID, FK to auth.users.id)
- roll_number
- branch
- batch_year
- current_year
- cgpa
- readiness_score
- total_problems_solved
- leetcode_stats (JSONB)
- codeforces_stats (JSONB)
- codechef_stats (JSONB)
- geeksforgeeks_stats (JSONB)
- hackerrank_stats (JSONB)
- skills (JSONB)
- preferred_roles (JSONB)
- expected_ctc_min
- expected_ctc_max
- resume_url
- portfolio_url
- linkedin_url
- created_at
- updated_at
- (and more...)

## Solutions

### Option 1: Revert Models to Match Current Database (Quick Fix)
**Pros:**
- Immediate fix
- No data migration needed
- Works with existing Supabase Auth

**Cons:**
- Keeps inconsistent naming
- May not align with best practices

**Steps:**
1. Revert `app/models/user.py` to use Supabase Auth schema
2. Revert all foreign keys back to match database types
3. Update column names to match database (e.g., `phone` instead of `phone_number`)

### Option 2: Create Migration to Update Database (Proper Fix)
**Pros:**
- Clean, consistent schema
- Follows SQLAlchemy best practices
- Better long-term maintainability

**Cons:**
- Requires careful migration planning
- Risk of data loss if not done correctly
- Downtime during migration

**Steps:**
1. Create Alembic migration to:
   - Rename columns in `auth.users` to match models
   - Ensure all ID types are UUID
   - Add any missing columns
2. Test migration on development database
3. Run migration on production

### Option 3: Use Supabase Auth Directly (Hybrid Approach)
**Pros:**
- Leverages Supabase's built-in auth
- Less custom code to maintain
- Better integration with Supabase ecosystem

**Cons:**
- Requires refactoring authentication logic
- May limit customization

**Steps:**
1. Update models to use Supabase's `auth.users` table directly
2. Use Supabase client for authentication
3. Keep custom tables (students, faculty, etc.) as-is

## Recommendation

For **immediate testing**, use **Option 1** (revert models).

For **production**, plan for **Option 2** (proper migration) with these steps:
1. Document current schema completely
2. Design target schema
3. Create migration scripts
4. Test on development database
5. Schedule maintenance window
6. Execute migration with rollback plan

## Files Modified (Need Reverting or Migration)

### Models Updated to UUID:
- `app/models/base.py` - BaseModel.id changed to UUID
- `app/models/user.py` - Uses custom column names
- `app/models/student.py` - user_id changed to UUID
- `app/models/faculty.py` - user_id changed to UUID
- `app/models/question.py` - created_by changed to UUID
- `app/models/assessment.py` - created_by, target_students changed to UUID
- `app/models/assessment_question.py` - assessment_id, question_id changed to UUID
- `app/models/submission.py` - student_id, question_id, assessment_attempt_id changed to UUID
- `app/models/assessment_attempt.py` - student_id, assessment_id changed to UUID

### Schemas Updated to UUID:
- `app/schemas/user.py` - id changed to UUID
- `app/schemas/student.py` - id, user_id changed to UUID

### Dependencies Updated:
- `app/api/deps.py` - Removed int() cast for UUID lookup

## Next Steps

**Immediate (to unblock testing):**
1. Decide on approach (revert vs migrate)
2. If reverting: Restore models to match database
3. If migrating: Create comprehensive migration plan

**Long-term:**
1. Standardize on either Supabase Auth or custom auth
2. Create proper migration strategy
3. Document schema decisions
4. Set up Alembic for future migrations
