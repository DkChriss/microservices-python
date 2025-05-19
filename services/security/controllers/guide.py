from fastapi import APIRouter, status, Query, Depends, HTTPException, Security
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from services.security.models.guide import Guide
from services.security.schemas.guide import GuideResponse, GuideUpdate, GuideStore
from services.security.utils.dependency import  get_db
from services.security.utils.security import get_current_user

router = APIRouter()

@router.get('/guides', status_code=status.HTTP_200_OK, tags=['guides'])
def list (
    page: int = Query(1, ge=1, description="Numero de pagina"),
    size: int = Query(10, ge=1, le=100, description="Guias por pagina"),
    db: Session = Depends(get_db),
    guide_permission: Guide = Security(get_current_user, scopes=["view guides"])
):
    try:
        params = Params(page=page, size=size)
        response = paginate(db.query(Guide), params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None
        return {
            "message": "Se ha obtenido la lista de guias correctamente",
            "data": [GuideResponse.model_validate(guide) for guide in response.items],
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/guides?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/guides?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/guides?page=1&size={size}",
                "last": f"/api/v1/guides?page={response.pages}&size={size}"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de guias {e}"
        )

@router.post(
    '/guides',
    status_code=status.HTTP_201_CREATED,
    tags=['guides']
)
def store (
        guide_store : GuideStore,
        db: Session = Depends(get_db),
        guide_permission: Guide = Security(get_current_user, scopes=["create guides"])
):
    try:
        new_guide = Guide(**guide_store.model_dump())
        db.add(new_guide)
        db.commit()
        db.refresh(new_guide)
        return {
            "message": "Se ha registrado la guia correctamente",
            "data": GuideResponse.model_validate(new_guide)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la guia {e}"
        )

@router.get('/guides/{id}', status_code=status.HTTP_200_OK, tags=['guides'])
def show(
        id: int,
        db: Session = Depends(get_db),
        guide_permission: Guide = Security(get_current_user, scopes=["show guide"])
):
    try:
        guide = db.query(Guide).filter(Guide.id == id).first()
        if guide is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la guia que desea obtener"
            )
        return {
            "message": "Se ha obtenido la guia correctamente",
            "data": GuideResponse.model_validate(guide)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la guia {e}"
        )

@router.put('/guides/{id}', status_code=status.HTTP_200_OK, tags=['guides'])
def update(
        id: int,
        guide_update : GuideUpdate,
        db: Session = Depends(get_db),
        guide_permission: Guide = Security(get_current_user, scopes=["update guides"])
):
    try:
        current_guide = db.query(Guide).filter(Guide.id == id).first()
        if guide_update is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la guia que desea actualizar"
            )
        guide_update.id = id
        for key, value in guide_update.model_dump(exclude_unset=True).items():
            setattr(current_guide, key, value)
        db.commit()
        db.refresh(current_guide)

        return {
            "message": "Se ha actualizado la guia correctamente",
            "data": GuideResponse.model_validate(current_guide)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la guia {e}"
        )


@router.delete('/guides/{id}', status_code=status.HTTP_200_OK, tags=['guides'])
def destroy(
        id: int,
        db: Session = Depends(get_db),
        guide_permission: Guide = Security(get_current_user, scopes=["delete guides"])
):
    try:
        current_guide = db.query(Guide).filter(Guide.id == id).first()
        if current_guide is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la guia que desea eliminar"
            )
        db.delete(current_guide)
        db.commit()
        return {
            "message": "Se ha eliminado la guia correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la guia {e}"
        )