from sqlalchemy import Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.security.config.database import Base
import datetime

class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer,primary_key=True, autoincrement=True)
    missing_id: Mapped[int] = mapped_column(Integer, ForeignKey('missing.id'))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text, nullable=True)
    phone: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(Text)
    date: Mapped[datetime.datetime] = mapped_column(DateTime)
    description: Mapped[Text] = mapped_column(Text)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    missing: Mapped["Missing"] = relationship("Missing", back_populates="reports")
    report_has_files: Mapped[list["ReportHasFiles"]] = relationship("ReportHasFiles", back_populates="report")
