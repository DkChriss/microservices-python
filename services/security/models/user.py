from sqlalchemy import  Integer, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.security.config.database import Base
from datetime import datetime
from zoneinfo import ZoneInfo
from services.security.models.status_enum import StatusEnum
from sqlalchemy import Enum as SQLEnum

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    code: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    last_name: Mapped[str] = mapped_column(Text)
    second_surname: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text, unique=True)
    avatar: Mapped[str] = mapped_column(Text)
    status: Mapped[StatusEnum] = mapped_column(
        SQLEnum(StatusEnum, name="status"),
        default=StatusEnum.online,
        nullable=False
    )
    password: Mapped[str] = mapped_column(Text)
    phone: Mapped[int] = mapped_column(Integer, unique=True)
    token_firebase: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("America/La_Paz")))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("America/La_Paz")), onupdate=datetime.now(ZoneInfo("America/La_Paz")))
    #N-M
    roles = relationship("Role", secondary='user_has_roles', back_populates="users", cascade="all")
    permissions = relationship("Permission", secondary='user_has_permissions', back_populates="users", cascade="all")
    #1-N
    guides = relationship("Guide", back_populates="user", cascade="all")
    faqs = relationship("Faq", back_populates="user", cascade="all")
    contacts_support = relationship("ContactSupport", back_populates="user", cascade="all")
    devices = relationship("Device", back_populates="user", cascade="all")
    emergency_contacts = relationship("EmergencyContact", back_populates="user", cascade="all")