from sqlalchemy import Integer, Text, DateTime, ForeignKey, JSON, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.security.config.database import Base
from datetime import datetime, date
from zoneinfo import ZoneInfo
from services.security.models.status_missing import StatusMissingEnum
from sqlalchemy import Enum as SQLEnum

class Missing(Base):
    __tablename__ = 'missing'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    name: Mapped[str] = mapped_column(Text)
    last_name: Mapped[str] = mapped_column(Text)
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    birthdate: Mapped[date] = mapped_column(Date)
    disappearance_date: Mapped[date] = mapped_column(Date)
    place_of_disappearance: Mapped[str] = mapped_column(Text)
    status_missing: Mapped[StatusMissingEnum] = mapped_column(
        SQLEnum(StatusMissingEnum, name="status_missing"),
        default=StatusMissingEnum.pending,
        nullable=False
    )
    photo: Mapped[str] = mapped_column(Text)
    characteristics: Mapped[str] = mapped_column(Text)
    reporter_name: Mapped[str] = mapped_column(Text)
    reporter_phone: Mapped[int] = mapped_column(Integer)
    event_photo: Mapped[str] = mapped_column(Text)
    location: Mapped[JSON] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("America/La_Paz")))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("America/La_Paz")), onupdate=datetime.now(ZoneInfo("America/La_Paz")))

    user = relationship("User", back_populates="missing")
