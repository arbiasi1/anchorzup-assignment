from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class Rule(Base):
    __tablename__ = "rules"
    __table_args__ = (
        CheckConstraint("match_type IN ('contains','startsWith','exact')", name="ck_rules_match_type"),
        CheckConstraint("action_type IN ('highlight','tooltip')", name="ck_rules_action_type"),
        CheckConstraint("priority >= 0 AND priority <= 100", name="ck_rules_priority"),
        Index("ix_rules_enabled_priority", "enabled", "priority"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255))
    match_type: Mapped[str] = mapped_column(String(20))
    action_type: Mapped[str] = mapped_column(String(20))
    color: Mapped[str | None] = mapped_column(String(7))
    label: Mapped[str | None] = mapped_column(String(100))
    priority: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    case_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
