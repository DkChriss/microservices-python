from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from config.database import engine
from models.permission import Permission
from models.role import Role
from models.user import User
from models.role_has_permissions import RoleHasPermissions
from models.user_has_roles import UserHasRoles
from models.user_has_permissions import UserHasPermissions
import json
import logging

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
    seed_model('seeders/data/permissions.json', Permission)
    seed_model('seeders/data/roles.json', Role)
    seed_model('seeders/data/users.json', User)
    seed_model('seeders/data/role_has_permissions.json', RoleHasPermissions)
    seed_model('seeders/data/user_has_permissions.json', UserHasPermissions)
    seed_model('seeders/data/user_has_roles.json', UserHasRoles)

