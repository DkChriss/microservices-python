from sqlalchemy import  Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.security.config.database import Base
from datetime import datetime
from zoneinfo import ZoneInfo
class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, unique=True)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("America/La_Paz")))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("America/La_Paz")), onupdate=datetime.now(ZoneInfo("America/La_Paz")))

    users = relationship("User", secondary='user_has_roles', back_populates="roles", cascade="all")
    permissions = relationship("Permission", secondary='role_has_permissions', back_populates="roles", cascade="all")