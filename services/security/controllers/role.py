from fastapi import APIRouter, Depends, HTTPException, Query, Form, status
from fastapi_pagination import Params
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, lazyload
from fastapi_pagination.ext.sqlalchemy import  paginate

from services.security.models.permission import Permission
from services.security.models.user import User
from services.security.utils.dependency import  get_db
from services.security.utils.mapper import map_to_schema
from services.security.models.role import Role
from services.security.schemas.roles import RoleStore, RoleUpdate, RoleUsers, RolePermissions, RoleResponse
router = APIRouter()

@router.get(
    '/roles',
    status_code=status.HTTP_200_OK,
    tags=["roles"]
)
def list(
        page: int = Query(1, ge=1, description="Numero de pagina"),
        size: int = Query(10, ge=1, le=100, description="Roles por pagina"),
        db: Session = Depends(get_db)
):
    try:
        params = Params(page=page, size=size)
        response = paginate(db.query(Role), params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None

        return {
            "message": "Se ha obtenido la lista de roles correctamente",
            "data": [RoleResponse.from_orm(role) for role in response.items],
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/roles?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/roles?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/roles?page=1&size={size}",
                "last": f"/api/v1/roles?page={response.pages}&size={size}"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de roles: {str(e)}"
        )
@router.post(
    "/roles",
    status_code=status.HTTP_201_CREATED,
    tags=["roles"]
)
def store(role_store: RoleStore, db: Session = Depends(get_db)):
    try:
        new_role = Role(**role_store.dict())
        db.add(new_role)
        db.commit()
        db.refresh(new_role)

        return {
            "message": "Se ha registrado el rol correctamente",
            "data": map_to_schema(new_role, RoleStore)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar el rol {e}"
        )

@router.get(
    "/roles/{id}",
    status_code=status.HTTP_200_OK,
    tags=["roles"]
)
def show(id: int, db: Session = Depends(get_db)):
    try:
        role = db.query(Role).filter(Role.id == id).first()
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el rol con que desea obtener"
            )

        return {
            "message": "Se ha obtenido el rol correctamente",
            "data": map_to_schema(role, RoleUpdate)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al obtener el rol: {e}"
        )

@router.put(
    "/roles/{id}",
    status_code=status.HTTP_200_OK,
    tags=["roles"]
)
def update(id: int ,role_update: RoleUpdate, db: Session = Depends(get_db)):
    try:
        current_role = db.query(Role).filter(Role.id == id).first()
        role_update.id = id
        if current_role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el rol que desea actualizar"
            )
        for key, value in role_update.dict(exclude_unset=True).items():
            setattr(current_role, key, value)
        db.commit()
        db.refresh(current_role)
        response = map_to_schema(current_role, RoleUpdate)
        return {
            "message": "Se ha actualizado el rol correctamente",
            "data": response
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al actualizar el rol: {e}"
        )

@router.delete(
    "/roles/{id}",
    status_code=status.HTTP_200_OK,
    tags=["roles"]
)
def destroy(id: int, db: Session = Depends(get_db)):
    try:
        role = db.query(Role).filter(Role.id == id).first()
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el rol que desea eliminar"
            )
        db.delete(role)
        db.commit()
        return {
            "message": "Se ha eliminado el rol correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al eliminar el rol: {e}"
        )

@router.post(
    '/roles/assign-users',
    status_code=status.HTTP_201_CREATED,
    tags=["roles"]
)
def assign_users(role_users: RoleUsers, db: Session = Depends(get_db)):
    try:
        current_role = db.query(Role).filter(Role.id == role_users.role_id).first()
        if current_role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el rol que desea asignar a los usuarios"
            )
        for id in role_users.users_ids:
            current_user = db.query(User).filter(User.id == id).first()
            if current_user is not None:
                current_user.roles.append(current_role)
                db.commit()
        return {
            "message": "Se ha asignado el rol a los usuarios correctamente",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error al asignar el rol a los usuarios"
        )
@router.post(
    '/roles/assign-permissions',
    status_code=status.HTTP_201_CREATED,
    tags=["roles"]
)
def assign_permissions(role_permissions: RolePermissions, db: Session = Depends(get_db)):
    try:
        current_role = db.query(Role).filter(Role.id == role_permissions.role_id).first()
        if current_role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el rol que desea asignar los permisos"
            )
        for id in role_permissions.permissions_ids:
            current_permission = db.query(Permission).filter(Permission.id == id).first()
            if current_permission is not None:
                current_role.permissions.append(current_permission)
                db.commit()
        return {
            "message": "Se ha asignado los permisos al rol correctamente",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error al asignar los permisos al rol"
        )