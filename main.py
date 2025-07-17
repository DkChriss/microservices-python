from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from config.database import Base, engine
from fastapi_pagination import add_pagination
#ROUTES
from controllers.user import router as user_router
from controllers.auth import router as auth_router
from controllers.role import router as role_router
from controllers.faq import router as faq_router
from controllers.category import router as category_router
from controllers.guide import router as guide_router
from controllers.contact_support import router as contact_router
from controllers.device import router as device_router
from controllers.device_registration import router as device_registration_router
from controllers.emergency_contact import router as emergency_contact_router
from controllers.request import router as request_router
from controllers.missing import router as missing_router
from controllers.permission import router as permission_router
from controllers.report import router as report_router
from controllers.public import router as public_router
#MODELS
from models.permission import Permission
from models.user import User
from models.role import Role
from models.user_has_permissions import UserHasPermissions
from models.role_has_permissions import RoleHasPermissions
from models.user_has_roles import UserHasRoles
from models.contact_support import ContactSupport
from models.category import Category
from models.guide import Guide
from models.faq import Faq
from models.device import Device
from models.device_registration import DeviceRegistration
from models.emergency_contact import EmergencyContact
from models.request import Request
from models.missing import Missing
from models.report import Report
from models.report_has_files import ReportHasFiles
#SEEDERS
from seeders.seed import seed
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
app.include_router(permission_router, prefix="/api/v1", tags=["permissions"])
app.include_router(category_router, prefix="/api/v1", tags=["categories"])
app.include_router(contact_router, prefix="/api/v1", tags=["contacts-support"])
app.include_router(guide_router, prefix="/api/v1", tags=["guides"])
app.include_router(faq_router, prefix="/api/v1", tags=["faqs"])
app.include_router(device_router, prefix="/api/v1", tags=["devices"])
app.include_router(device_registration_router, prefix="/api/v1", tags=["devices-registration"])
app.include_router(emergency_contact_router, prefix="/api/v1", tags=["emergency-contacts"])
app.include_router(request_router, prefix="/api/v1", tags=["requests"])
app.include_router(missing_router, prefix="/api/v1", tags=["missing"])
app.include_router(report_router, prefix="/api/v1", tags=["reports"])
app.include_router(public_router, prefix="/api/v1/public")
add_pagination(app)
