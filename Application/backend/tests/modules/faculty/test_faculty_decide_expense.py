from app.database.enums import *
from db_factory.factory import *


# -------------------------------------------------------------------
# Test: Successfully approve an expense
# -------------------------------------------------------------------
def test_approve_expense_success(
    client,
    auth_headers,
    faculty_advisor_user,
    db_session
):
    headers = auth_headers(faculty_advisor_user.email)

    university = UniversityFactory()
    user = UserFactory()

    club = ClubFactory(
        university=university,
        faculty_advisor=faculty_advisor_user,
    )

    budget = BudgetFactory(
        club=club,
        creator=faculty_advisor_user
    )

    expense = ExpenseFactory(
        budget=budget,
        submitter=user,
        approval_status=ExpenseStatus.PENDING,
    )

    response = client.patch(
        f"/api/faculty/expenses/{expense.id}/decision",
        headers=headers,
        json={
            "approval_status": ExpenseStatus.APPROVED.value,
            "status": "APPROVED",
            "approval_remarks": "Approved",
            "approved_by": faculty_advisor_user.id,
        },
    )

    assert response.status_code == 200

    db_session.refresh(expense)

    assert expense.approval_status == ExpenseStatus.APPROVED
    assert expense.status == ExpenseStatus.APPROVED
    assert expense.approved_by == faculty_advisor_user.id


# -------------------------------------------------------------------
# Test: Successfully reject an expense
# -------------------------------------------------------------------
def test_reject_expense_success(
    client,
    auth_headers,
    faculty_advisor_user,
    db_session,
):
    headers = auth_headers(faculty_advisor_user.email)

    university = UniversityFactory()
    user = UserFactory()

    club = ClubFactory(
        university=university,
        faculty_advisor=faculty_advisor_user,
    )

    budget = BudgetFactory(
        club=club,
        creator=faculty_advisor_user
    )

    expense = ExpenseFactory(
        budget=budget,
        submitter=user,
        approval_status=ExpenseStatus.PENDING,
    )

    response = client.patch(
        f"/api/faculty/expenses/{expense.id}/decision",
        headers=headers,
        json={
            "approval_status": ExpenseStatus.REJECTED.value,
            "status": ExpenseStatus.REJECTED,
            "approval_remarks": "Budget exceeded",
            "approved_by": faculty_advisor_user.id,
        },
    )

    assert response.status_code == 200

    db_session.refresh(expense)

    assert expense.approval_status == ExpenseStatus.REJECTED
    assert expense.status == ExpenseStatus.REJECTED


# -------------------------------------------------------------------
# Test: Advisor cannot approve another advisor's expense
# -------------------------------------------------------------------
def test_expense_decision_forbidden(
    client,
    auth_headers,
    faculty_advisor_user,
):
    headers = auth_headers(faculty_advisor_user.email)

    another_advisor = UserFactory(
        role=UserRole.FACULTY_ADVISOR,
    )

    university = UniversityFactory()
    user = UserFactory()

    club = ClubFactory(
        university=university,
        faculty_advisor=another_advisor,
    )

    budget = BudgetFactory(
        club=club,
        creator=another_advisor
    )

    expense = ExpenseFactory(
        budget=budget,
        submitter=user,
        approval_status=ExpenseStatus.PENDING,
    )

    response = client.patch(
        f"/api/faculty/expenses/{expense.id}/decision",
        headers=headers,
        json={
            "approval_status": ExpenseStatus.APPROVED.value,
            "status": ExpenseStatus.APPROVED,
        },
    )

    assert response.status_code == 403
    assert "unauthorized" in response.get_json()["message"].lower()



# -------------------------------------------------------------------
# Test: Unauthorized request
# -------------------------------------------------------------------
def test_expense_decision_unauthorized(client):

    response = client.patch(
        "/api/faculty/expenses/1/decision",
        json={
            "approval_status": ExpenseStatus.APPROVED.value,
            "status": ExpenseStatus.APPROVED,
        },
    )

    assert response.status_code == 401


# -------------------------------------------------------------------
# Test: Wrong role
# -------------------------------------------------------------------
def test_expense_decision_wrong_role(
    client,
    auth_headers,
    student_user,
):
    headers = auth_headers(student_user.email)

    response = client.patch(
        "/api/faculty/expenses/1/decision",
        headers=headers,
        json={
            "approval_status": ExpenseStatus.APPROVED.value,
            "status": ExpenseStatus.APPROVED,
        },
    )

    assert response.status_code == 403


# -------------------------------------------------------------------
# Test: Database exception
# -------------------------------------------------------------------
def test_expense_decision_database_error(
    client,
    auth_headers,
    faculty_advisor_user,
    db_error,
):
    import app.modules.faculty.routes as faculty_module
    db_error(faculty_module)

    headers = auth_headers(faculty_advisor_user.email)

    response = client.patch(
        "/api/faculty/expenses/1/decision",
        headers=headers,
        json={
            "approval_status": ExpenseStatus.APPROVED.value,
            "status": ExpenseStatus.APPROVED,
        },
    )

    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]