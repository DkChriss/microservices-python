from sqlalchemy import Table, Column, ForeignKey

from services.security.config.database import Base

user_has_permissions = Table(
    'user_has_permissions',
    Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('permission_id', ForeignKey('permissions.id'), primary_key=True)
)

user_has_roles = Table(
    'user_has_roles',
    Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('role_id', ForeignKey('roles.id'), primary_key=True)
)

role_has_permissions = Table(
    'role_has_permissions',
    Base.metadata,
    Column('role_id', ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', ForeignKey('permissions.id'), primary_key=True)
)