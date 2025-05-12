from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from services.security.config.database import Base, engine
from services.security.controllers.user import router as user_router
from services.security.controllers.auth import router as auth_router
from fastapi_pagination import add_pagination

#IMPORT MODELS FOR CREATING TABLES
from services.security.models.permission import Permission
from services.security.models.user import User
from services.security.models.role import Role
from services.security.models.association import *
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
app.include_router(user_router, prefix="/api/v1", tags=["users"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
add_pagination(app)
