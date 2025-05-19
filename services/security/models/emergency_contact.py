from sqlalchemy import Integer,DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.security.config.database import Base
from datetime import datetime
from zoneinfo import ZoneInfo

class EmergencyContact(Base):
    __tablename__ = 'emergency_contacts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    name: Mapped[str] = mapped_column(Text)
    line: Mapped[str] = mapped_column(Text)
    phone: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("America/La_Paz")))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("America/La_Paz")), onupdate=datetime.now(ZoneInfo("America/La_Paz")))

    user = relationship("User", back_populates="emergency_contacts")
