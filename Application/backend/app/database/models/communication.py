"""Communication / shared-resource module: notifications and documents."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from ..base import Base
from ..enums import DocumentType, NotificationChannel, NotificationType


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(SAEnum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    channel = Column(SAEnum(NotificationChannel), default=NotificationChannel.IN_APP, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    sent_via_resend = Column(Boolean, default=False, nullable=False)
    related_entity_type = Column(String(100), nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="notifications")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    committee_id = Column(Integer, ForeignKey("committees.id", ondelete="SET NULL"), nullable=True)
    doc_type = Column(SAEnum(DocumentType), nullable=False)
    file_url = Column(Text, nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="documents", foreign_keys=[owner_id])
    committee = relationship("Committee", foreign_keys=[committee_id])
    club = relationship("Club", foreign_keys=[club_id])
    event= relationship("Event", foreign_keys=[event_id])
