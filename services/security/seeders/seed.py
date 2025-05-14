from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from services.security.config.database import engine
from services.security.models.permission import Permission
from services.security.models.role import Role
from services.security.models.user import User
import json

def seed_model(path: str, BaseModel, engine = engine):
    print(f"Seeding model: {BaseModel.__name__} from {path}")

    session = Session(bind=engine)

    try:
        with open(path) as f:
            data = json.load(f)

        for entry in data:
            entity = BaseModel(**entry)
            session.add(entity)

        session.commit()
        print("Seeding completed successfully.")

    except IntegrityError as e:
        session.rollback()
        print(f"IntegrityError: {e}")

    except Exception as e:
        session.rollback()
        print(f"Error seeding model: {e}")

    finally:
        session.close()
        print("Session closed.")

def seed():
    seed_model('services/security/seeders/data/permissions.json', Permission)
    seed_model('services/security/seeders/data/roles.json', Role)
    seed_model('services/security/seeders/data/users.json', User)