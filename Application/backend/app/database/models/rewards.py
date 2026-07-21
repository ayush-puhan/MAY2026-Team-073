"""Rewards module: reward points ledger and reward redemptions."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from ..base import Base
from ..enums import RedemptionStatus


class RewardPointsLedger(Base):
    """Append-only ledger; balance = SUM(points) per user (never an updatable running total)."""

    __tablename__ = "reward_points_ledger"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    points = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)
    source_event_id = Column(Integer, ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])


class RewardRedemption(Base):
    __tablename__ = "reward_redemptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    points_spent = Column(Integer, nullable=False)
    reward_description = Column(Text, nullable=False)
    status = Column(SAEnum(RedemptionStatus), default=RedemptionStatus.REQUESTED, nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approved_by])


class RewardTask(Base):
    __tablename__ = "reward_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    points = Column(Integer, nullable=False)
    type = Column(String(50), nullable=False)  # daily, weekly, monthly, one_time
    icon = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    is_active = Column(Integer, default=1, nullable=False)
    max_completions = Column(Integer, default=1, nullable=False)
    requires_verified = Column(Integer, default=0, nullable=False)


class RewardTaskCompletion(Base):
    __tablename__ = "reward_task_completions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(Integer, ForeignKey("reward_tasks.id", ondelete="CASCADE"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    task = relationship("RewardTask", foreign_keys=[task_id])


class RewardStoreItem(Base):
    __tablename__ = "reward_store_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    points_cost = Column(Integer, nullable=False)
    category = Column(String(100), nullable=True)
    icon = Column(String(100), nullable=True)
    stock = Column(Integer, default=0, nullable=False)
    max_per_user = Column(Integer, default=1, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    requires_verified = Column(Integer, default=0, nullable=False)
