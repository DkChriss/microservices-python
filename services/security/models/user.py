
from sqlalchemy import Column, Integer, PrimaryKeyConstraint, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.security.config.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    codigo: Mapped[str] = mapped_column(Text)
    nombre: Mapped[str] = mapped_column(Text)
    apellido_paterno: Mapped[str] = mapped_column(Text)
    apellido_materno: Mapped[str] = mapped_column(Text)
    correo_electronico: Mapped[str] = mapped_column(Text, unique=True)
    avatar: Mapped[str] = mapped_column(Text)
    estado: Mapped[bool] = mapped_column(Boolean, default=False)
    contraseña: Mapped[str] = mapped_column(Text)
    celular: Mapped[int] = mapped_column(Integer, unique=True)
    token_firebase: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)