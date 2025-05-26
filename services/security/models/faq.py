from sqlalchemy import Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.security.config.database import Base
from datetime import datetime
from zoneinfo import ZoneInfo

class Faq(Base):
    __tablename__ = 'faqs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("America/La_Paz")))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("America/La_Paz")), onupdate=datetime.now(ZoneInfo("America/La_Paz")))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'))

    user = relationship("User", back_populates="faqs")
    category = relationship("Category", back_populates="faqs")