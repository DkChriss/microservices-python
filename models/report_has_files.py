from sqlalchemy import Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from config.database import Base
import datetime

class ReportHasFiles(Base):
    __tablename__ = "report_has_files"

    id: Mapped[int] = mapped_column(Integer,primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    report_id: Mapped[int] = mapped_column(Integer, ForeignKey('reports.id'))

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    report: Mapped["Report"] = relationship("Report", back_populates="report_has_files")
