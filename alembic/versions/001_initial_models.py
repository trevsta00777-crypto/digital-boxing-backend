"""Initial models including Payment

Revision ID: 001_initial
Revises:
Create Date: 2026-09-10

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_id", "users", ["id"])

    op.create_table(
        "fighters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("nickname", sa.String(255), nullable=True),
        sa.Column("weight_class", sa.String(50), nullable=False),
        sa.Column("height", sa.Float(), nullable=True),
        sa.Column("reach", sa.Float(), nullable=True),
        sa.Column("wins", sa.Integer(), server_default="0"),
        sa.Column("losses", sa.Integer(), server_default="0"),
        sa.Column("draws", sa.Integer(), server_default="0"),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_fighters_id", "fighters", ["id"])

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("event_date", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(50), server_default="Scheduled"),
        sa.Column("ticket_price_cents", sa.Integer(), server_default="0"),
        sa.Column("currency", sa.String(10), server_default="usd"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_events_id", "events", ["id"])

    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id"), nullable=True),
        sa.Column("fighter1_id", sa.Integer(), sa.ForeignKey("fighters.id"), nullable=False),
        sa.Column("fighter2_id", sa.Integer(), sa.ForeignKey("fighters.id"), nullable=False),
        sa.Column("rounds", sa.Integer(), server_default="12"),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(50), server_default="Scheduled"),
        sa.Column("winner_id", sa.Integer(), sa.ForeignKey("fighters.id"), nullable=True),
        sa.Column("fighter1_score", sa.Integer(), nullable=True),
        sa.Column("fighter2_score", sa.Integer(), nullable=True),
        sa.Column("result", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("match_date", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_matches_id", "matches", ["id"])

    op.create_table(
        "training_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("fighter_id", sa.Integer(), sa.ForeignKey("fighters.id"), nullable=True),
        sa.Column("session_type", sa.String(100), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("exercises", sa.String(500), nullable=True),
        sa.Column("intensity", sa.String(50), server_default="Medium"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("calories_burned", sa.Integer(), nullable=True),
        sa.Column("session_date", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_training_sessions_id", "training_sessions", ["id"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id"), nullable=True),
        sa.Column("payment_type", sa.String(50), server_default="event_ticket"),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(10), server_default="usd"),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("stripe_checkout_session_id", sa.String(255), nullable=True),
        sa.Column("stripe_payment_intent_id", sa.String(255), nullable=True),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_payments_id", "payments", ["id"])
    op.create_index(
        "ix_payments_stripe_checkout_session_id",
        "payments",
        ["stripe_checkout_session_id"],
        unique=True,
    )
    op.create_index(
        "ix_payments_stripe_payment_intent_id",
        "payments",
        ["stripe_payment_intent_id"],
    )


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_table("training_sessions")
    op.drop_table("matches")
    op.drop_table("events")
    op.drop_table("fighters")
    op.drop_table("users")
