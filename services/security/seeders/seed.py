import logging

from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from services.security.config.database import engine
from services.security.models.permission import Permission
from services.security.models.role import Role
from services.security.models.user import User
from services.security.models.role_has_permissions import RoleHasPermissions
from services.security.models.user_has_roles import UserHasRoles
from services.security.models.user_has_permissions import UserHasPermissions
import json

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def seed_model(path: str, BaseModel, engine = engine):
    logging.info(f"Seeding model: {BaseModel.__name__} from {path}")

    session = Session(bind=engine)

    try:
        with open(path) as f:
            data = json.load(f)

        for entry in data:
            entity = BaseModel(**entry)
            if hasattr(entity, "password"):
                hashed_password = bcrypt_context.hash(entity.password)
                entity.password = hashed_password
            session.add(entity)

        session.commit()
        logging.info("Seeding completed successfully.")

    except IntegrityError as e:
        session.rollback()
        logging.error(f"IntegrityError: {e}")

    except Exception as e:
        session.rollback()
        logging.error(f"Error seeding model: {e}")

    finally:
        session.close()
        logging.info("Session closed.")

def seed():
    seed_model('services/security/seeders/data/permissions.json', Permission)
    seed_model('services/security/seeders/data/roles.json', Role)
    seed_model('services/security/seeders/data/users.json', User)
    seed_model('services/security/seeders/data/role_has_permissions.json', RoleHasPermissions)
    seed_model('services/security/seeders/data/user_has_permissions.json', UserHasPermissions)
    seed_model('services/security/seeders/data/user_has_roles.json', UserHasRoles)

