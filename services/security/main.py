from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from services.security.config.database import Base, engine
from fastapi_pagination import add_pagination
#ROUTES
from services.security.controllers.user import router as user_router
from services.security.controllers.auth import router as auth_router
from services.security.controllers.role import router as role_router
from services.security.controllers.faq import router as faq_router
from services.security.controllers.category import router as category_router
from services.security.controllers.guide import router as guide_router
from services.security.controllers.contact_support import router as contact_router
from services.security.controllers.device import router as device_router
from services.security.controllers.device_registration import router as device_registration_router
#MODELS
from services.security.models.permission import Permission
from services.security.models.user import User
from services.security.models.role import Role
from services.security.models.user_has_permissions import UserHasPermissions
from services.security.models.role_has_permissions import RoleHasPermissions
from services.security.models.user_has_roles import UserHasRoles
from services.security.models.contact_support import ContactSupport
from services.security.models.category import Category
from services.security.models.guide import Guide
from services.security.models.faq import Faq
from services.security.models.device import Device
from services.security.models.device_registration import DeviceRegistration
#SEEDERS
from services.security.seeders.seed import seed
import os

debug = os.getenv("DEBUG", "False").lower() == "true"
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
if debug:
    Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
# SEEDING
seed()
#ROUTES
app.include_router(user_router, prefix="/api/v1", tags=["users"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(role_router, prefix="/api/v1", tags=["roles"])
app.include_router(category_router, prefix="/api/v1", tags=["categories"])
app.include_router(contact_router, prefix="/api/v1", tags=["contacts-support"])
app.include_router(guide_router, prefix="/api/v1", tags=["guides"])
app.include_router(faq_router, prefix="/api/v1", tags=["faqs"])
app.include_router(device_router, prefix="/api/v1", tags=["devices"])
app.include_router(device_registration_router, prefix="/api/v1", tags=["devices-registration"])
add_pagination(app)
