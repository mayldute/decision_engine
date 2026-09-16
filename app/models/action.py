import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    # TO DO: add type (set a value, send an email and etc.)
    # BY DEFAULT: SET
    field: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[str | float | int | bool] = mapped_column(
        JSONB, nullable=False
    )

    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rules.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    rule: Mapped["Rule"] = relationship(
        back_populates="action",
    )
