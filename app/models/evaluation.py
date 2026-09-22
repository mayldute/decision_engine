import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    input: Mapped[dict] = mapped_column(JSONB, nullable=False)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    user: Mapped["User"] = relationship(back_populates="evaluations")

    evaluation_rules: Mapped[list["EvaluationRule"]] = relationship(
        back_populates="evaluation",
    )
