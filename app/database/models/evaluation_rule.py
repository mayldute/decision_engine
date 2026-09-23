import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.evaluation import Evaluation
    from app.database.models.rule import Rule


class EvaluationRule(Base):
    __tablename__ = "evaluation_rules"

    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evaluations.id", ondelete="CASCADE"),
        primary_key=True,
    )

    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rules.id", ondelete="CASCADE"),
        primary_key=True,
    )

    is_matched: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    resulting_input: Mapped[dict] = mapped_column(JSONB, nullable=False)

    evaluation: Mapped["Evaluation"] = relationship(
        back_populates="evaluation_rules",
    )

    rule: Mapped["Rule"] = relationship(
        back_populates="evaluation_rules",
    )
