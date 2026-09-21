import uuid

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import ComparisonOperator
from app.models.rules_conditions import rule_condition_association


class Condition(Base):
    __tablename__ = "conditions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    field: Mapped[str] = mapped_column(String(50), nullable=False)
    operator: Mapped[ComparisonOperator] = mapped_column(
        Enum(ComparisonOperator),
        nullable=False,
    )
    value: Mapped[str | float | int | bool] = mapped_column(JSONB, nullable=False)

    rules: Mapped[list["Rule"]] = relationship(
        secondary=rule_condition_association, back_populates="conditions"
    )
