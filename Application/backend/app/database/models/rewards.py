"""Rewards module: reward points ledger and reward redemptions."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..enums import RedemptionStatus


class RewardPointsLedger(Base):
    """Append-only ledger; balance = SUM(points) per user (never an updatable running total)."""

    __tablename__ = "reward_points_ledger"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    source_event_id: Mapped[Optional[int]] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class RewardRedemption(Base):
    __tablename__ = "reward_redemptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    points_spent: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[RedemptionStatus] = mapped_column(
        SAEnum(RedemptionStatus), default=RedemptionStatus.REQUESTED, nullable=False
    )
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    approver: Mapped[Optional["User"]] = relationship(foreign_keys=[approved_by])
