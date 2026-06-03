"""add_question_import_jobs_and_question_source

Revision ID: e7b9c4d1a2f0
Revises: f32b80d2cc28
Create Date: 2026-04-06 12:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "e7b9c4d1a2f0"
down_revision: Union[str, None] = "f32b80d2cc28"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new first-class difficulty level.
    op.execute("ALTER TYPE difficulty_level ADD VALUE IF NOT EXISTS 'expert'")

    # Track the source of a question (AI Generated, Manual, Imported, etc.).
    op.add_column(
        "questions",
        sa.Column(
            "source",
            sa.String(length=100),
            nullable=True,
            comment="Question source: AI Generated, Manual, Imported",
        ),
    )

    file_type_enum = postgresql.ENUM(
        "xlsx",
        "csv",
        "pdf",
        name="question_import_file_type",
        create_type=False,
    )
    status_enum = postgresql.ENUM(
        "pending",
        "processing",
        "awaiting_review",
        "completed",
        "failed",
        name="question_import_status",
        create_type=False,
    )
    bind = op.get_bind()
    file_type_enum.create(bind, checkfirst=True)
    status_enum.create(bind, checkfirst=True)

    op.create_table(
        "question_import_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("faculty_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_type", file_type_enum, nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            status_enum,
            nullable=False,
            server_default=sa.text("'pending'::question_import_status"),
        ),
        sa.Column("total_rows", sa.Integer(), nullable=True),
        sa.Column("imported_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "failed_rows",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "parsed_preview",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["faculty_id"], ["auth.users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "idx_question_import_jobs_faculty_id",
        "question_import_jobs",
        ["faculty_id"],
        unique=False,
    )
    op.create_index(
        "idx_question_import_jobs_status",
        "question_import_jobs",
        ["status"],
        unique=False,
    )
    op.create_index(
        "idx_question_import_jobs_created_at",
        "question_import_jobs",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_question_import_jobs_created_at", table_name="question_import_jobs")
    op.drop_index("idx_question_import_jobs_status", table_name="question_import_jobs")
    op.drop_index("idx_question_import_jobs_faculty_id", table_name="question_import_jobs")
    op.drop_table("question_import_jobs")

    op.execute("DROP TYPE IF EXISTS question_import_status")
    op.execute("DROP TYPE IF EXISTS question_import_file_type")

    op.drop_column("questions", "source")

    # Revert enum by remapping expert questions to hard.
    op.execute("UPDATE questions SET difficulty = 'hard' WHERE difficulty = 'expert'")
    op.execute("ALTER TYPE difficulty_level RENAME TO difficulty_level_old")
    op.execute("CREATE TYPE difficulty_level AS ENUM ('easy', 'medium', 'hard')")
    op.execute(
        "ALTER TABLE questions ALTER COLUMN difficulty TYPE difficulty_level "
        "USING difficulty::text::difficulty_level"
    )
    op.execute("DROP TYPE difficulty_level_old")
