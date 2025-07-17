from sqlalchemy import Column, ForeignKey, Integer
from config.database import Base

class UserHasRoles(Base):

    __tablename__ = 'user_has_roles'

    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)