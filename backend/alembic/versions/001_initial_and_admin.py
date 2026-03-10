"""Initial schema and default administrator.

Revision ID: 001
Revises:
Create Date: Initial

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("hashed_password", sa.String(256), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "cars",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("make", sa.String(128), nullable=True),
        sa.Column("model", sa.String(256), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("color", sa.String(64), nullable=True),
        sa.Column("link", sa.String(512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cars_link", "cars", ["link"], unique=True)
    op.create_index("ix_cars_make", "cars", ["make"], unique=False)
    op.create_index("ix_cars_model", "cars", ["model"], unique=False)
    op.create_index("ix_cars_year", "cars", ["year"], unique=False)

    # Seed default administrator (username: admin, password: admin123)
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_ctx.hash("admin123")
    op.execute(
        sa.text(
            "INSERT INTO users (username, hashed_password) VALUES ('admin', :hp)"
        ).bindparams(hp=hashed)
    )


def downgrade() -> None:
    op.drop_index("ix_cars_year", "cars")
    op.drop_index("ix_cars_model", "cars")
    op.drop_index("ix_cars_make", "cars")
    op.drop_index("ix_cars_link", "cars")
    op.drop_table("cars")
    op.drop_index("ix_users_username", "users")
    op.drop_table("users")
