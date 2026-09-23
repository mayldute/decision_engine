import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.models.enums import LogicalOperator
from app.database.models.evaluation_rule import EvaluationRule
from app.database.models.rules_conditions import rule_condition_association

if TYPE_CHECKING:
    from app.database.models.action import Action
    from app.database.models.condition import Condition
    from app.database.models.evaluation_rule import EvaluationRule
    from app.database.models.user import User


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    logical_operator: Mapped[LogicalOperator | None] = mapped_column(
        Enum(LogicalOperator), nullable=True
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("priority >= 1 AND priority <= 100"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=True,
    )

    conditions: Mapped[list["Condition"]] = relationship(
        secondary=rule_condition_association, back_populates="rules"
    )

    action_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("actions.id"),
        nullable=False,
    )

    action: Mapped["Action"] = relationship(back_populates="rules")

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    user: Mapped["User"] = relationship(back_populates="rules")

    evaluation_rules: Mapped[list["EvaluationRule"]] = relationship(
        back_populates="rule",
    )
