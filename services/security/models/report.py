from sqlalchemy import Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.security.config.database import Base
import datetime

class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer,primary_key=True, autoincrement=True)
    missing_id: Mapped[int] = mapped_column(Integer, ForeignKey('missing.id'))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    reporter_name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text)
    phone: Mapped[int] = mapped_column(Integer )