from sqlalchemy import Table, Column, Integer, ForeignKey

from services.security.config.database import Base

role_has_permissions = Table(
    'role_has_permissions',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

user_has_permissions = Table(
    'user_has_permissions',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

user_has_roles = Table(
    'user_has_roles',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)