from pydantic import ConfigDict
from sqlalchemy import Integer,DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.security.config.database import Base
from datetime import datetime
from zoneinfo import ZoneInfo

class DeviceRegistration(Base):
    __tablename__ = "devices_registration"
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Mapped[int] = mapped_column(Integer,primary_key=True, autoincrement=True)
    location: Mapped[JSON] = mapped_column(JSON)
    wifi: Mapped[str] = mapped_column(Text)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey('devices.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("America/La_Paz")))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("America/La_Paz")), onupdate=datetime.now(ZoneInfo("America/La_Paz")))

    device = relationship("Device", back_populates="devices_registration")
