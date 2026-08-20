"""Financial management module: budgets and expenses (with embedded
single-lifecycle approval fields).


Frontend-matching endpoints:
  GET    /api/budgets?club_id=<id>
  POST   /api/budgets
  PATCH  /api/budgets/<id>


  GET    /api/expenses?budget_id=<id>
  PATCH  /api/expenses/<id>
"""


from datetime import datetime


from flask import Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import get_jwt_identity


from app.database.database import get_session
from app.database.models import Budget, Expense
from app.database.enums import (
    BudgetStatus,
    ExpenseStatus,
    ExpenseApprovalStatus,
    ClubMemberRole,
)
from app.middleware.auth_middleware import require_auth, require_club_role, require_club_role_or_faculty_advisor



# -------------------------------------------------
# Blueprint
# -------------------------------------------------


budget_bp = Blueprint("budgets", __name__)
api = Api(budget_bp)



# -------------------------------------------------
# Serializers
# -------------------------------------------------


def serialize_budget(budget: Budget) -> dict:
    return {
        "id": str(budget.id),
        "club_id": budget.club_id,
        "committee_id": budget.committee_id,
        "parent_budget_id": budget.parent_budget_id,
        "title": budget.title,
        "period_start": budget.period_start.strftime("%Y-%m-%d"),
        "period_end": budget.period_end.strftime("%Y-%m-%d"),
        "allocated_amount": float(budget.allocated_amount),
        "status": budget.status.value,
        "created_by": budget.created_by,
        "created_at": budget.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }



def serialize_expense(expense: Expense) -> dict:
    return {
        "id": expense.id,
        "budget_id": expense.budget_id,
        "description": expense.description,
        "amount": float(expense.amount),
        "category": expense.category,
        "submitted_by": expense.submitted_by,
        "status": expense.status.value,
        "approval_status": expense.approval_status.value,
        "approved_by": expense.approved_by,
        "approval_date": (
            expense.approval_date.isoformat()
            if expense.approval_date
            else None
        ),
        "approval_remarks": expense.approval_remarks,
        "created_at": expense.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }



# =================================================
# BUDGETS
# GET    /budgets?club_id=<id>
# POST   /budgets
# PATCH  /budgets/<id>
# =================================================


class BudgetListResource(Resource):
    """
    GET  /budgets?club_id=<id>
    POST /budgets
    """

    @require_auth
    @require_club_role_or_faculty_advisor(
        ClubMemberRole.TREASURER,
        ClubMemberRole.PRESIDENT,
        ClubMemberRole.VICE_PRESIDENT
    )
    def get(self):
        try:
            with get_session() as session:
                club_id = request.args.get("club_id")
                query = session.query(Budget)

                if club_id:
                    query = query.filter(Budget.club_id == int(club_id))

                budgets = query.all()
                # Return plain JSON array
                return [serialize_budget(b) for b in budgets], 200
        except Exception as e:
            return {'message' : f'ERROR {e}'},500

    @require_auth
    @require_club_role_or_faculty_advisor(
        ClubMemberRole.TREASURER,
        ClubMemberRole.PRESIDENT
    )
    def post(self):
        try:
            with get_session() as session:
                data = request.get_json() or {}

                # Required fields
                required_fields = ["club_id", "allocated_amount"]
                for field in required_fields:
                    if field not in data:
                        return {"message": f"Missing field: {field}"}, 400

                club_id = int(data["club_id"])
                committee_id = data.get("committee_id")

                # Committee budgets inherit dates from the main club budget
                if committee_id:
                    parent_budget = (
                        session.query(Budget)
                        .filter(
                            Budget.club_id == club_id,
                            Budget.committee_id.is_(None),
                            Budget.parent_budget_id.is_(None),
                        )
                        .first()
                    )

                    if not parent_budget:
                        return {
                            "message": "Main club budget not found. Create it first."
                        }, 400

                    if parent_budget.allocated_amount < float(data["allocated_amount"]):
                        return {
                            "message": "Insufficient main budget"
                        }, 400

                    parent_budget.allocated_amount -= float(data["allocated_amount"])
                    
                    budget = Budget(
                        club_id=club_id,
                        committee_id=int(committee_id),
                        parent_budget_id=parent_budget.id,
                        title=data.get("title", "Committee Budget"),
                        allocated_amount=float(data["allocated_amount"]),
                        period_start=parent_budget.period_start,
                        period_end=parent_budget.period_end,
                        status=BudgetStatus.APPROVED,
                        created_by=get_jwt_identity(),
                    )
                    
                    session.add(parent_budget)

                # Main club budget
                else:
                    required_dates = ["period_start", "period_end"]
                    for field in required_dates:
                        if field not in data:
                            return {"message": f"Missing field: {field}"}, 400

                    budget = Budget(
                        club_id=club_id,
                        title=data.get("title", "Main Club Budget"),
                        allocated_amount=float(data["allocated_amount"]),
                        period_start=datetime.fromisoformat(data["period_start"]),
                        period_end=datetime.fromisoformat(data["period_end"]),
                        status=BudgetStatus.APPROVED,
                        created_by=get_jwt_identity(),
                    )

                session.add(budget)
                session.commit()

                return serialize_budget(budget), 201
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500


class BudgetUpdateResource(Resource):
    """
    PATCH /budgets/<id>
    """

    @require_auth
    @require_club_role_or_faculty_advisor(
        ClubMemberRole.TREASURER,
        ClubMemberRole.PRESIDENT
    )

    def patch(self, budget_id: int):
        try:
            with get_session() as session:
                budget = (
                    session.query(Budget)
                    .filter(Budget.id == budget_id)
                    .first()
                )
                if not budget:
                    return {"message": "Budget not found"}, 404

                data = request.get_json() or {}

                if "allocated_amount" in data:
                    budget.allocated_amount = float(data["allocated_amount"])

                session.commit()
                return serialize_budget(budget), 200
        except Exception as e:
            return {'message' : f"Database error : {e}"},500



# =================================================
# EXPENSES
# GET    /expenses?budget_id=<id>
# PATCH  /expenses/<id>
# =================================================


class ExpenseListResource(Resource):
    """
    GET  /expenses?budget_id=<id>
    POST /expenses
    """

    @require_auth
    @require_club_role(
        ClubMemberRole.MEMBER,
        ClubMemberRole.TREASURER,
        ClubMemberRole.PRESIDENT,
        ClubMemberRole.VICE_PRESIDENT
    )
    def get(self):
        try:
            with get_session() as session:
                budget_id = request.args.get("budget_id")
                club_id = request.args.get("club_id")
                
                query = session.query(Expense)

                if budget_id:
                    query = query.filter(Expense.budget_id == int(budget_id))
                
                if club_id:
                    query = query.join(Budget).filter(Budget.club_id == int(club_id))

                expenses = query.all()
                return [serialize_expense(e) for e in expenses], 200
        except Exception as e:
            return {'message' : f"Database error : {e}"},500

    @require_auth
    @require_club_role(
        ClubMemberRole.TREASURER,
        ClubMemberRole.PRESIDENT
    )
    def post(self):
        try:
            with get_session() as session:
                data = request.get_json() or {}

                required_fields = [
                    "budget_id",
                    "description",
                    "amount",
                ]

                for field in required_fields:
                    if field not in data:
                        return {"message": f"Missing field: {field}"}, 400

                budget = (
                    session.query(Budget)
                    .filter(Budget.id == int(data["budget_id"]))
                    .first()
                )

                if not budget:
                    return {"message": "Budget not found"}, 404

                expense = Expense(
                    budget_id=budget.id,
                    description=data["description"],
                    amount=float(data["amount"]),
                    category=data.get("category"),
                    submitted_by=get_jwt_identity(),

                    # Initial state
                    status=ExpenseStatus.PENDING,
                    approval_status=ExpenseApprovalStatus.PENDING,
                )

                session.add(expense)
                session.commit()

                return serialize_expense(expense), 201
        except Exception as e:
            return {'message' : f"Error : {e}"}, 500


class ExpenseUpdateResource(Resource):
    """
    PATCH /expenses/<id>
    Used by facultyAdvisorApi.decideExpense to update approval fields.
    """

    @require_auth
    @require_club_role(
        ClubMemberRole.TREASURER,
        ClubMemberRole.PRESIDENT
    )

    def patch(self, expense_id: int):
        try:
            with get_session() as session:
                expense = (
                    session.query(Expense)
                    .filter(Expense.id == expense_id)
                    .first()
                )
                if not expense:
                    return {"message": "Expense not found"}, 404

                data = request.get_json() or {}

                # Map frontend fields to model fields
                if "approval_status" in data:
                    expense.approval_status = ExpenseApprovalStatus(data["approval_status"])

                if "status" in data:
                    expense.status = ExpenseStatus(data["status"])

                if "approval_remarks" in data:
                    expense.approval_remarks = data["approval_remarks"]

                if "approved_by" in data:
                    expense.approved_by = int(data["approved_by"])

                # Set approval_date if not already set
                if expense.approval_date is None:
                    expense.approval_date = datetime.utcnow()

                session.commit()
                return serialize_expense(expense), 200
        except Exception as e:
            return {'message' : f"ERROR : {e}"}, 500


# =================================================
# ROUTES
# =================================================


api.add_resource(BudgetListResource, "/budgets")
api.add_resource(BudgetUpdateResource, "/budgets/<int:budget_id>")


api.add_resource(ExpenseListResource, "/expenses")
api.add_resource(ExpenseUpdateResource, "/expenses/<int:expense_id>")