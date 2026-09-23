import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.evaluation import Evaluation
    from app.database.models.rule import Rule
    from app.database.models.token import RefreshToken


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    nickname: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    rules: Mapped[list["Rule"]] = relationship(back_populates="user")

    evaluations: Mapped[list["Evaluation"]] = relationship(back_populates="user")

    refresh_token: Mapped["RefreshToken"] = relationship(
        "RefreshToken",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
