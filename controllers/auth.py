import jwt.exceptions
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from models.user import User
from schemas.auth import Token
from schemas.user import UserResponse
from utils.dependency import get_db
import os
import jwt
router = APIRouter()

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE = timedelta(minutes=60)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/auth/login", status_code=status.HTTP_200_OK, response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.phone == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El numero de celular o contraseña estan incorrectas"
        )
    try:
        if not verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El numero de celular o contraseña estan incorrectas"
            )
        roles = []
        permissions = []

        for role in user.roles:
            if role.name not in roles:
                roles.append(role.name)
            #ROLE PERMISSIONS
            for permission in role.permissions:
                if permission.action not in permissions:
                    permissions.append(permission.action)

        #USER HAS PERMISSIONS
        for permission in user.permissions:
            if permission.action not in permissions:
                permissions.append(permission.action)

        token = create_access_token(user.phone, ACCESS_TOKEN_EXPIRE, user.id, permissions, roles)
        return {
            'token': token,
            'token_type': 'bearer',
            'user': UserResponse.model_validate(user),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar las credenciales {e}"
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)

def create_access_token(username: int, expires_delta: timedelta,  user_id: int, scopes: list[str], roles: list[str]):
    encode = {'sub': str(username), 'id': user_id, 'scopes': scopes, 'roles': roles}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)