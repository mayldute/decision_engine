from sqlalchemy import Column, ForeignKey, Table

from app.database.base import Base

rule_condition_association = Table(
    "rule_condition_association",
    Base.metadata,
    Column("rule_id", ForeignKey("rules.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "condition_id",
        ForeignKey("conditions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
