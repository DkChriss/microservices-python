from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from passlib.exc import InvalidTokenError
from sqlalchemy.orm import Session
from typing import List
#MODELS
from services.security.models.role import Role
from services.security.models.user import User
from services.security.utils.dependency import get_db
#ALL
import os
import jwt

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={
        "view users": "view users",
        "create users": "create users",
        "show user": "show user",
        "update users": "update users",
        "delete users": "delete users",
        "view roles": "view roles",
        "create roles": "create roles",
        "show role": "show role",
        "update roles": "update roles",
        "delete roles": "delete roles",
        "assign roles": "assign roles",
        "assign permissions": "assign_permissions"
    }
)

async def get_current_user(
        security_scopes: SecurityScopes,
        token: str = Depends(oauth2_bearer),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No esta autorizado para realizar esta accion",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        scopes = payload.get("scopes", [])
        roles = payload.get("roles", [])
        user = db.query(User).filter(User.id == payload.get("id")).first()
        if user is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    if scopes == [] and roles == []:
        raise credentials_exception
    add_permissions(scopes, roles, db)
    check_permissions(scopes, security_scopes, "Su usuario no tiene los permisos necesarios para realizar esta accion")

def add_permissions(scopes: List[str], roles: List[str], db: Session):
    if not roles == []:
        for role in roles:
            current_role = db.query(Role).filter(Role.name == role).first()
            if current_role is not None:
                actions: list[str] = [permission.action for permission in current_role.permissions]
                scopes = list(set(actions) | set(scopes))

def check_permissions(permissions: List[str],  security_scopes: SecurityScopes, message: str):
    if not permissions == []:
        for scope in security_scopes.scopes:
            if scope not in permissions:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)