from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Query, Depends, HTTPException, Security
from services.security.schemas.permissions import PermissionResponse
from services.security.utils.dependency import  get_db
from services.security.utils.security import get_current_user
from services.security.models.permission import Permission
from fastapi_pagination import Params

router = APIRouter()

@router.get('/permissions', status_code=status.HTTP_200_OK, tags=['permissions'])
def list (
    page: int = Query(1, ge=1, description="Numero de pagina"),
    size: int = Query(10, ge=1, le=100, description="Permiso por pagina"),
    search: str = Query("", description="Buscar permiso"),
    db: Session = Depends(get_db),
    permission: Permission = Security(get_current_user, scopes=["view permissions"])
):
    try:
        params = Params(page=page, size=size)
        query = db.query(Permission)
        if search:
            query = query.filter(
                or_(
                    Permission.name.like(f'%{search}%'),
                    Permission.action.like(f'%{search}%'),
                    Permission.model.like(f'%{search}%'),
                )
            ).order_by(Permission.id)
        response = paginate(query, params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None

        return {
            "message": "Se ha obtenido la lista de permisos correctamente",
            "data": [PermissionResponse.model_validate(permission) for permission in response.items],
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/permissions?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/permissions?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/permissions?page=1&size={size}",
                "last": f"/api/v1/permissions?page={response.pages}&size={size}"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de roles: {str(e)}"
        )