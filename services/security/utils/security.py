import os

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from passlib.exc import InvalidTokenError
from starlette import status

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={
        "view:users": "view users",
        "create:users": "create users",
        "show:user": "show user",
        "update:users": "update users",
        "delete:users": "delete users",
        "view:roles": "view roles",
        "create:roles": "create roles",
        "show:role": "show role",
        "update:roles": "update roles",
        "delete:roles": "delete roles",
        "assign:roles": "assign roles",
        "assign:permissions": "assign permissions"
    }
)

async def get_current_user( security_scopes: SecurityScopes, token: str = Depends(oauth2_bearer)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No esta autorizado para realizar esta accion",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        scopes = payload.get("scopes", [])
        roles = payload.get("roles", [])
        id = payload.get("id")
        if scopes == [] or roles == [] or id is None:
            raise credentials_exception
        return {
            "id": id,
            "roles": roles,
            "scopes": scopes,
        }
    except InvalidTokenError:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene los permisos necesarios para realizar esta accion")

    return {"sub": username, "scopes": token_scopes}
