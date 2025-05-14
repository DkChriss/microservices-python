import json

from fastapi import APIRouter, Depends, HTTPException, Query, Form, status
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user

from services.security.models.permission import Permission
from services.security.models.role import Role
from services.security.schemas.user import UserStore, UserUpdate, UserRoles, UserPermissions
from services.security.utils.dependency import  get_db
from services.security.models.user import User
from services.security.utils.mapper import map_to_schema

router = APIRouter()
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

@router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    tags=["users"]
)
def list(
        page: int = Query(1, ge=1, description="Numero de pagina"),
        size: int = Query(10, ge=1, le=100, description="Usuarios por pagina"),
        db: Session = Depends(get_db)
):
    try:
        params = Params(page=page, size=size)
        response = paginate(db.query(User), params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None

        return {
            "message": "Se ha obtenido la lista de usuarios correctamente",
            "data": response.items,
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/users?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/users?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/users?page=1&size={size}",
                "last": f"/api/v1/users?page={response.pages}&size={size}"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de usuarios: {str(e)}"
        )
@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
)
def store(user: UserStore, db: Session = Depends(get_db)):
    try:
        hashed_password = bcrypt_context.hash(user.password)
        user.password = hashed_password
        new_user = User(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "Se ha registrado el usuario correctamente",
            "data": new_user
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al registrar el usuario: {e}"
        )
@router.get(
    "/users/{id}",
    status_code=status.HTTP_200_OK,
    tags=["users"]
)
def show(id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el usuario con que desea obtener"
            )

        return {
            "message": "Se ha obtenido el usuario correctamente",
            "data": user
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al obtener el usuario: {e}"
        )
@router.put(
    "/users/{id}",
    status_code=status.HTTP_200_OK,
    tags=["users"]
)
def update(id: int ,user_update: UserUpdate, db: Session = Depends(get_db)):
    try:
        current_user = db.query(User).filter(User.id == id).first()
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el usuario que desea actualizar"
            )
        user_update.id = id
        for key, value in user_update.dict(exclude_unset=True).items():
            setattr(current_user, key, value)
        db.commit()
        db.refresh(current_user)
        response = map_to_schema(current_user, UserStore)
        return {
            "message": "Se ha actualizado el usuario correctamente",
            "data": response
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al actualizar el usuario: {e}"
        )
@router.delete(
    "/users/{id}",
    status_code=status.HTTP_200_OK,
    tags=["users"]
)
def destroy(id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el usuario que desea eliminar"
            )
        db.delete(user)
        db.commit()
        return {
            "message": "Se ha eliminado el usuario correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al eliminar el usuario: {e}"
        )

@router.post(
    '/users/assign-roles',
    status_code=status.HTTP_201_CREATED,
    tags=["users"]
)
def assign_roles(user_roles:UserRoles, db: Session = Depends(get_db)):
    try:
        current_user = db.query(User).filter(User.id == user_roles.user_id).first()
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el usuario que desea asignar los roles"
            )
        for id in user_roles.roles_ids:
            current_role = db.query(Role).filter(Role.id == id).first()
            if current_role is not None:
                current_user.roles.append(current_role)
                db.commit()
        return {
            "message": "Se ha asignado los roles al usuario correctamente",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al asignar los roles al usuario: {e}"
        )

@router.post(
    '/users/assign-permissions',
    status_code=status.HTTP_201_CREATED,
    tags=["users"]
)
def assign_permissions(user_permissions: UserPermissions, db: Session = Depends(get_db)):
    try:
        current_user = db.query(User).filter(User.id == user_permissions.user_id).first()
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='No existe el usuario que desea asignar los permissions'
            )
        for id in user_permissions.permissions_ids:
            current_permission = db.query(Permission).filter(Permission.id == id).first()
            if current_permission is not None:
                current_user.permissions.append(current_permission)
                db.commit()

        return {
            "message": "Se ha asignado los permissions al usuario correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error al asignar los permisos al usuario"
        )