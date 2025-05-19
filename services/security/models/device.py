from sqlalchemy import Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.security.config.database import Base
from datetime import datetime
from zoneinfo import ZoneInfo

class Device(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(Integer,primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)
    password: Mapped[str] = mapped_column(Text)
    status: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("America/La_Paz")))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("America/La_Paz")), onupdate=datetime.now(ZoneInfo("America/La_Paz")))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="devices")
    devices_registration = relationship("DeviceRegistration", back_populates="device", cascade="all")