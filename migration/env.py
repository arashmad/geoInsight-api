from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# ! important => import models so Alembic registers them in Base.metadata
import geoinsight_api.db.models  # noqa: F401
from geoinsight_api.core.config import settings
from geoinsight_api.db.base import Base

config = context.config

config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


POSTGIS_INTERNAL_TABLES = {
    "spatial_ref_sys",
    "topology",
    "layer",
}


def include_object(object_, name, type_, reflected, compare_to):
    """
    Prevent Alembic from trying to drop PostGIS-owned internal tables.

    reflected=True means the object exists in the database.
    compare_to=None means the object does not exist in SQLAlchemy metadata.
    """
    if type_ == "table" and reflected and name in POSTGIS_INTERNAL_TABLES:
        return False

    return True


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        include_object=include_object,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
