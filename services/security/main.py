from fastapi import FastAPI
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from services.security.config.database import Base, engine
from fastapi_pagination import add_pagination
#ROUTES
from services.security.controllers.user import router as user_router
from services.security.controllers.auth import router as auth_router
from services.security.controllers.role import router as role_router
#MODELS
from services.security.models.permission import Permission
from services.security.models.user import User
from services.security.models.role import Role
from services.security.models.user_role import UserRole
from services.security.models.role_permission import RolePermission
from services.security.models.user_permission import UserPermission
app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CREATE TABLES
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

#ROUTES
app.include_router(user_router, prefix="/api/v1", tags=["users"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(role_router, prefix="/api/v1", tags=["roles"])
add_pagination(app)
