from sqlalchemy import Column, ForeignKey, Integer
from services.security.config.database import Base

class UserHasPermissions(Base):

    __tablename__ = 'user_has_permissions'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id'), primary_key=True)