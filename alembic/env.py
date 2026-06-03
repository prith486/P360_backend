from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.core.config import settings
from app.models.base import Base

# Import all models here for autogenerate
from app.models.auth_user import AuthUser
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.admin_activity import AdminActivityLog
from app.models.question import Question
from app.models.assessment import Assessment
from app.models.assessment_question import AssessmentQuestion
from app.models.submission import Submission
from app.models.assessment_attempt import AssessmentAttempt
from app.models.question_import_job import QuestionImportJob

# Alembic Config object
config = context.config

# Set database URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model metadata for autogenerate
target_metadata = Base.metadata

def include_object(object, name, type_, reflected, compare_to):
    """
    Only include the public schema.
    """
    if type_ == "table":
        return object.schema == "public" or object.schema is None
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
