
from sqlalchemy import Column, Integer, PrimaryKeyConstraint, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.security.config.database import Base
import datetime

from services.security.models.role import Role


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    code: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    last_name: Mapped[str] = mapped_column(Text)
    second_surname: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text, unique=True)
    avatar: Mapped[str] = mapped_column(Text)
    status: Mapped[bool] = mapped_column(Boolean, default=False)
    password: Mapped[str] = mapped_column(Text)
    phone: Mapped[int] = mapped_column(Integer, unique=True)
    token_firebase: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    roles = relationship("Role", secondary='user_has_roles', back_populates="users", cascade="all")
    permissions = relationship("Permission", secondary='user_has_permissions', back_populates="users", cascade="all")
