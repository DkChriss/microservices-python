from fastapi import APIRouter, status, Query, Depends, HTTPException, Security
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from services.security.models.request import Request
from services.security.schemas.request import RequestResponse, RequestUpdate, RequestStore
from services.security.utils.dependency import  get_db
from services.security.utils.security import get_current_user

router = APIRouter()

@router.get(
    '/requests',
    status_code=status.HTTP_200_OK,
    tags=['requests']
)
def list (
    page: int = Query(1, ge=1, description="Numero de pagina"),
    size: int = Query(10, ge=1, le=100, description="Solicitudes por pagina"),
    db: Session = Depends(get_db),
    request_permission: Request = Security(get_current_user, scopes=["view requests"])
):
    try:
        params = Params(page=page, size=size)
        response = paginate(db.query(Request),params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None
        return {
            "message": "Se ha obtenido la lista de solicitudes correctamente",
            "data": [RequestResponse.model_validate(request) for request in response.items],
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/requests?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/requests?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/requests?page=1&size={size}",
                "last": f"/api/v1/requests?page={response.pages}&size={size}"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de solicitudes {e}"
        )

@router.post(
    '/requests',
    status_code=status.HTTP_201_CREATED,
    tags=['requests']
)
def store (
        request_store : RequestStore,
        db: Session = Depends(get_db),
        request_permission: Request = Security(get_current_user, scopes=["create requests"])
):
    try:
        new_request = Request(**request_store.model_dump())
        db.add(new_request)
        db.commit()
        db.refresh(new_request)
        return {
            "message": "Se ha registrado la solicitud correctamente",
            "data": RequestResponse.model_validate(new_request)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la solicitud {e}"
        )

@router.get(
    '/requests/{id}',
    status_code=status.HTTP_200_OK,
    tags=['requests']
)
def show(
        id: int,
        db: Session = Depends(get_db),
        request_permission: Request = Security(get_current_user, scopes=["show request"])
):
    try:
        request = db.query(Request).filter(Request.id == id).first()
        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la solicitud que desea obtener"
            )
        return {
            "message": "Se ha obtenido la solicitud correctamente",
            "data": RequestResponse.model_validate(request)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la solicitud {e}"
        )

@router.put(
    '/requests/{id}',
    status_code=status.HTTP_200_OK,
    tags=['requests']
)
def update(
        id: int,
        request_update : RequestUpdate,
        db: Session = Depends(get_db),
        request_permission: Request = Security(get_current_user, scopes=["update requests"])
):
    try:
        current_request = db.query(Request).filter(Request.id == id).first()
        if current_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la solicitud que desea actualizar"
            )
        request_update.id = id
        for key, value in request_update.model_dump(exclude_unset=True).items():
            setattr(current_request, key, value)
        db.commit()
        db.refresh(current_request)

        return {
            "message": "Se ha actualizado la solicitud",
            "data": RequestResponse.model_validate(current_request)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la solicitud {e}"
        )


@router.delete(
    '/requests/{id}',
    status_code=status.HTTP_200_OK,
    tags=['requests']
)
def destroy(
        id: int,
        db: Session = Depends(get_db),
        request_permission: Request = Security(get_current_user, scopes=["delete requests"])
):
    try:
        current_request = db.query(Request).filter(Request.id == id).first()
        if current_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la solicitud que desea eliminar"
            )
        db.delete(current_request)
        db.commit()
        return {
            "message": "Se ha eliminado la solicitud correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la solicitud {e}"
        )