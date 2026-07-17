"""University model for multi-tenant support."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..base import Base
from ..mixins import SoftDeleteMixin, TimestampMixin


class University(Base, TimestampMixin, SoftDeleteMixin):
    """Tenant entity representing a registered university on the platform."""

    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False)
    short_name = Column(String(50), nullable=True)
    logo_url = Column(Text, nullable=True)
    domain = Column(String(100), unique=True, nullable=False)
    address = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    banner = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    users = relationship("User", back_populates="university")
    departments = relationship("Department", back_populates="university")
    clubs = relationship("Club", back_populates="university")
    tickets = relationship("SupportTicket", back_populates="university")
    allowed_domains = relationship("UniversityDomain", back_populates="university", cascade="all, delete-orphan")


class UniversityDomain(Base, TimestampMixin):
    """Allowed email domains for a university."""

    __tablename__ = "university_domains"

    id = Column(Integer, primary_key=True, autoincrement=True)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    domain = Column(String(100), nullable=False)

    university = relationship("University", back_populates="allowed_domains")
