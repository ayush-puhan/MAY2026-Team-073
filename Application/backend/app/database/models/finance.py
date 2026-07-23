"""Financial management module: budgets and expenses (with embedded
single-lifecycle approval fields)."""

from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from ..base import Base
from ..enums import BudgetStatus, ExpenseApprovalStatus, ExpenseStatus


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        CheckConstraint("period_end >= period_start", name="ck_budget_period"),
        CheckConstraint("allocated_amount >= 0", name="ck_budget_amount_nonneg"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    committee_id = Column(Integer, ForeignKey("committees.id", ondelete="CASCADE"), nullable=True)
    parent_budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    allocated_amount = Column(Numeric(12, 2), default=0, nullable=False)
    status = Column(SAEnum(BudgetStatus), default=BudgetStatus.DRAFT, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    club = relationship("Club", back_populates="budgets")
    committee = relationship("Committee", backref="budgets")
    parent_budget = relationship("Budget", remote_side=[id], backref="sub_budgets")
    creator = relationship("User", foreign_keys=[created_by])
    expenses = relationship("Expense", back_populates="budget", cascade="all, delete-orphan")


class Expense(Base):
    """Single, non-polymorphic approval lifecycle embedded directly on the expense
    (approval_status / approved_by / approval_date / approval_remarks) rather than
    a separate FinancialApproval table."""

    __tablename__ = "expenses"
    __table_args__ = (CheckConstraint("amount > 0", name="ck_expense_amount_positive"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    category = Column(String(100), nullable=True)
    receipt_document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    submitted_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    status = Column(SAEnum(ExpenseStatus), default=ExpenseStatus.PENDING, nullable=False)

    # Embedded single-lifecycle approval fields (replaces FinancialApproval table)
    approval_status = Column(
        SAEnum(ExpenseApprovalStatus), default=ExpenseApprovalStatus.PENDING, nullable=False
    )
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    approval_remarks = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    budget = relationship("Budget", back_populates="expenses")
    receipt_document = relationship("Document", foreign_keys=[receipt_document_id])
    submitter = relationship("User", foreign_keys=[submitted_by])
    approver = relationship("User", foreign_keys=[approved_by])
