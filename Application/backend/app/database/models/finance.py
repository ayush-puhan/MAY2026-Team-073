"""Financial management module: budgets and expenses (with embedded
single-lifecycle approval fields)."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..enums import BudgetStatus, ExpenseApprovalStatus, ExpenseStatus


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        CheckConstraint("period_end >= period_start", name="ck_budget_period"),
        CheckConstraint("allocated_amount >= 0", name="ck_budget_amount_nonneg"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    period_start: Mapped[datetime] = mapped_column(nullable=False)
    period_end: Mapped[datetime] = mapped_column(nullable=False)
    allocated_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    status: Mapped[BudgetStatus] = mapped_column(SAEnum(BudgetStatus), default=BudgetStatus.DRAFT, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    club: Mapped["Club"] = relationship(back_populates="budgets")
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    expenses: Mapped[List["Expense"]] = relationship(back_populates="budget", cascade="all, delete-orphan")


class Expense(Base):
    """Single, non-polymorphic approval lifecycle embedded directly on the expense
    (approval_status / approved_by / approval_date / approval_remarks) rather than
    a separate FinancialApproval table."""

    __tablename__ = "expenses"
    __table_args__ = (CheckConstraint("amount > 0", name="ck_expense_amount_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    budget_id: Mapped[int] = mapped_column(ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    receipt_document_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    submitted_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[ExpenseStatus] = mapped_column(SAEnum(ExpenseStatus), default=ExpenseStatus.PENDING, nullable=False)

    # Embedded single-lifecycle approval fields (replaces FinancialApproval table)
    approval_status: Mapped[ExpenseApprovalStatus] = mapped_column(
        SAEnum(ExpenseApprovalStatus), default=ExpenseApprovalStatus.PENDING, nullable=False
    )
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approval_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    approval_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    budget: Mapped["Budget"] = relationship(back_populates="expenses")
    receipt_document: Mapped[Optional["Document"]] = relationship(foreign_keys=[receipt_document_id])
    submitter: Mapped["User"] = relationship(foreign_keys=[submitted_by])
    approver: Mapped[Optional["User"]] = relationship(foreign_keys=[approved_by])
