"""Academic module: departments, programs, and per-student academic profiles."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from ..base import Base


class Department(Base):
    """Central master table for university departments."""

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=True)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    programs = relationship("Program", back_populates="department", cascade="all, delete-orphan")
    users = relationship("User", back_populates="department")
    university = relationship("University", back_populates="departments")


class Program(Base):
    """University academic program, scoped to a department."""

    __tablename__ = "programs"
    __table_args__ = (UniqueConstraint("department_id", "name", name="uq_program_name_per_department"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    department = relationship("Department", back_populates="programs")
    student_profiles = relationship("StudentProfile", back_populates="program")


class StudentProfile(Base):
    """Student-specific academic details, in a strict 1:1 relationship with User."""

    __tablename__ = "student_profiles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    program_id = Column(Integer, ForeignKey("programs.id", ondelete="RESTRICT"), nullable=False)
    academic_year = Column(Integer, nullable=True)
    semester = Column(Integer, nullable=True)
    batch = Column(String(20), nullable=True)
    section = Column(String(10), nullable=True)
    institutional_email = Column(String(255), unique=True, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="student_profile")
    program = relationship("Program", back_populates="student_profiles")
