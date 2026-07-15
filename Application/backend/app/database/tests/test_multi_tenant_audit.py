import pytest
from sqlalchemy.exc import IntegrityError
from app.database.models.audit import AuditLog
from app.database.models.university import University, UniversityDomain
from app.database.models.auth import User
from app.database.enums import UserRole

def test_create_university(session):
    """Test creating a new university tenant."""
    uni = University(
        name="Global Tech University",
        domain="globaltech.edu",
        is_active=True
    )
    session.add(uni)
    session.commit()
    
    assert uni.id is not None
    assert uni.name == "Global Tech University"
    # Ensure TimestampMixin worked
    assert uni.created_at is not None

def test_create_university_domain(session):
    """Test creating a university domain."""
    uni = University(name="State College", domain="state.edu")
    session.add(uni)
    session.commit()
    
    domain = UniversityDomain(university_id=uni.id, domain="students.state.edu")
    session.add(domain)
    session.commit()
    
    assert domain.id is not None
    assert domain.university.name == "State College"
    assert domain.domain == "students.state.edu"

def test_audit_log_creation(session):
    """Test tracking an action in the audit log."""
    # 1. Create a mock user
    user = User(
        email="admin@test.edu",
        password_hash="hashed_pw",
        full_name="System Admin",
        role=UserRole.SYSTEM_ADMIN
    )
    session.add(user)
    session.commit()
    
    # 2. Create an audit log for that user
    log = AuditLog(
        user_id=user.id,
        action="SYSTEM_UPDATE",
        entity_type="PlatformSettings",
        details="Changed default theme to dark mode"
    )
    session.add(log)
    session.commit()
    
    assert log.id is not None
    assert log.user.email == "admin@test.edu"
    assert log.action == "SYSTEM_UPDATE"
    # Ensure TimestampMixin worked
    assert log.created_at is not None

def test_audit_log_user_deletion_set_null(session):
    """Test that deleting a user sets their audit log user_id to NULL (referential integrity)."""
    user = User(email="test2@test.edu", password_hash="hash", full_name="Test", role=UserRole.STUDENT)
    session.add(user)
    session.commit()
    
    log = AuditLog(user_id=user.id, action="LOGIN")
    session.add(log)
    session.commit()
    
    session.delete(user)
    session.commit()
    
    session.refresh(log)
    assert log.user_id is None
