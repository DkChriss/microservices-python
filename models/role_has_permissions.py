from sqlalchemy import Column, ForeignKey, Integer
from config.database import Base

class RoleHasPermissions(Base):

    __tablename__ = 'role_has_permissions'

    role_id = Column(Integer, ForeignKey('roles.id', ondelete="CASCADE"), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id'), primary_key=True)