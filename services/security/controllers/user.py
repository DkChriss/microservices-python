from fastapi import APIRouter, Depends, HTTPException, Query, status, Security, Form, UploadFile, File
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.orm import Session
from services.security.models.permission import Permission
from services.security.models.role import Role
from services.security.models.status_enum import StatusEnum
from services.security.schemas.user import UserRoles, UserPermissions, UserResponse
from services.security.utils.dependency import  get_db
from services.security.models.user import User
from services.security.utils.security import get_current_user
from services.security.utils.files import save_avatar_file
import os
import shutil
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
        db: Session = Depends(get_db),
        user_permission: User = Security(get_current_user, scopes=["view users"])
):
    try:
        params = Params(page=page, size=size)
        response = paginate(db.query(User), params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None

        return {
            "message": "Se ha obtenido la lista de usuarios correctamente",
            "data": [UserResponse.model_validate(user) for user in response.items],
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
    tags=["users"]
)
def store(
        code: str = Form(...),
        name: str = Form(...),
        last_name: str = Form(...),
        second_surname: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(...),
        phone: int = Form(...),
        token_firebase: str = Form(None),
        user_status: StatusEnum = Form(...),
        avatar: UploadFile = File(...),
        db: Session = Depends(get_db),
        user_permission: User = Security(get_current_user, scopes=["create users"])
):
    saved_avatar_path = None

    try:
        relative_avatar_path = save_avatar_file(avatar, name, last_name, code)
        saved_avatar_path = os.path.join("services", "security", relative_avatar_path)

        hashed_password = bcrypt_context.hash(password)

        new_user = User(
            code=code,
            name=name,
            last_name=last_name,
            second_surname=second_surname,
            email=email,
            avatar=relative_avatar_path,
            status=user_status,
            password=hashed_password,
            phone=phone,
            token_firebase=token_firebase or ""
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "Se ha registrado el usuario correctamente",
            "data": UserResponse.model_validate(new_user)
        }

    except Exception as e:
        db.rollback()
        if saved_avatar_path and os.path.exists(saved_avatar_path):
            os.remove(saved_avatar_path)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al registrar el usuario: {e}"
        )
@router.get(
    "/users/{id}",
    status_code=status.HTTP_200_OK,
    tags=["users"]
)
def show(
        id: int,
        db: Session = Depends(get_db),
        user_permission: User = Security(get_current_user, scopes=["show user"])
):
    try:
        user = db.query(User).filter(User.id == id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el usuario con que desea obtener"
            )

        return {
            "message": "Se ha obtenido el usuario correctamente",
            "data": UserResponse.model_validate(user)
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
def update(
        id: int,
        code: str = Form(...),
        name: str = Form(...),
        last_name: str = Form(...),
        second_surname: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(None),
        phone: int = Form(...),
        token_firebase: str = Form(None),
        user_status: StatusEnum = Form(...),
        avatar: UploadFile = File(None),
        db: Session = Depends(get_db),
        user_permission: User = Security(get_current_user, scopes=["update users"])
):
    new_avatar_path = None

    try:
        current_user = db.query(User).filter(User.id == id).first()
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el usuario que desea actualizar"
            )

        if avatar:
            new_relative_avatar_path = save_avatar_file(avatar, name, last_name, code)
            new_avatar_path = os.path.join("services", "security", new_relative_avatar_path)

            old_avatar_path = os.path.join("services", "security", current_user.avatar)
            if os.path.exists(old_avatar_path) and old_avatar_path != new_avatar_path:
                os.remove(old_avatar_path)

            current_user.avatar = new_relative_avatar_path

        # Update other fields
        current_user.code = code
        current_user.name = name
        current_user.last_name = last_name
        current_user.second_surname = second_surname
        current_user.email = email
        current_user.status = user_status
        current_user.phone = phone
        current_user.token_firebase = token_firebase or current_user.token_firebase

        if password:
            current_user.password = bcrypt_context.hash(password)

        db.commit()
        db.refresh(current_user)

        return {
            "message": "Se ha actualizado el usuario correctamente",
            "data": UserResponse.model_validate(current_user)
        }

    except Exception as e:
        db.rollback()
        if new_avatar_path and os.path.exists(new_avatar_path):
            os.remove(new_avatar_path)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al actualizar el usuario: {e}"
        )
@router.delete(
    "/users/{id}",
    status_code=status.HTTP_200_OK,
    tags=["users"]
)
def destroy(
        id: int,
        db: Session = Depends(get_db),
        user_permission: User = Security(get_current_user, scopes=["delete users"])
):
    try:
        user = db.query(User).filter(User.id == id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el usuario que desea eliminar"
            )
        db.delete(user)
        db.commit()
        avatar_path = os.path.join("services", "security", user.avatar)
        if os.path.exists(avatar_path):
            os.remove(avatar_path)
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
def assign_roles(
        user_roles:UserRoles,
        db: Session = Depends(get_db),
        user_permission: User = Security(get_current_user, scopes=["assign roles"])
):
    try:
        current_user = db.query(User).filter(User.id == user_roles.user_id).first()
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el usuario que desea asignar los roles"
            )
        for id in user_roles.roles_ids:
            current_role = db.query(Role).filter(Role.id == id).first()
            if current_role is not None and current_role not in current_user.roles:
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
def assign_permissions(
        user_permissions: UserPermissions,
        db: Session = Depends(get_db),
        user_permission: User = Security(get_current_user, scopes=["assign permissions"])
):
    try:
        current_user = db.query(User).filter(User.id == user_permissions.user_id).first()
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='No existe el usuario que desea asignar los permissions'
            )
        for id in user_permissions.permissions_ids:
            current_permission = db.query(Permission).filter(Permission.id == id).first()
            if current_permission is not None and current_permission not in current_user.permissions:
                current_user.permissions.append(current_permission)
                db.commit()

        return {
            "message": "Se ha asignado los permissions al usuario correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al asignar los permisos al usuario {e}"
        )