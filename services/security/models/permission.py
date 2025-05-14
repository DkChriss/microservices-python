from sqlalchemy import Column, Integer, PrimaryKeyConstraint, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.security.config.database import Base
import datetime

class Permission(Base):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, unique=True)
    action: Mapped[str] = mapped_column(Text, unique=True)
    model: Mapped[str] = mapped_column(Text, unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    users = relationship("User", secondary='user_has_permissions', back_populates="permissions", cascade="all")
    roles = relationship("Role", secondary='role_has_permissions', back_populates="permissions", cascade="all")
