from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv
import os
import jwt

from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from passlib.context import CryptContext
from datetime import timedelta, datetime
from sqlalchemy.orm import Session

from services.security.models.user import User
from services.security.schemas.auth import Token, TokenData
from services.security.utils.dependency import get_db

router = APIRouter()

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE = timedelta(minutes=60)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={
        "view users": "view users",
        "create users": "create users",
        "show user": "show users",
        "update users": "update users",
        "delete users": "delete users",
        "view roles": "view roles",
        "create roles": "create roles",
        "show role": "show role",
        "update roles": "update roles",
        "delete roles": "delete roles",
        "assign roles": "assign roles",
        "assign permissions": "assign permissions"
    }
)

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
        roles = [role.name for role in user.roles]
        permissions = [permission.action for permission in user.permissions]
        token = create_access_token(user.phone, ACCESS_TOKEN_EXPIRE, user.id, permissions, roles)
        return {
            'access_token': token,
            'token_type': 'bearer',
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar las credenciales {e}"
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)

def create_access_token(username: int, expires_delta: timedelta,  user_id: int, scopes: list[str], roles: list[str]):
    encode = {'sub': username, 'id': user_id, 'scopes': scopes, 'roles': roles}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
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

