from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..base import Base
from ..mixins import TimestampMixin

class AuditLog(Base, TimestampMixin):
    """Tracks administrative and significant user actions across the platform."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(Integer, nullable=True)
    
    details = Column(Text, nullable=True)
    
    # Relationship to user
    user = relationship("User", backref="audit_logs")
