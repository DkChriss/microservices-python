from fastapi import APIRouter, status, Query, Depends, HTTPException, Security
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from services.security.models.category import Category
from services.security.models.faq import Faq
from services.security.models.user import User
from services.security.schemas.faq import FaqResponse, FaqUpdate, FaqStore
from services.security.utils.dependency import  get_db
from services.security.utils.security import get_current_user

router = APIRouter()

@router.get('/faqs', status_code=status.HTTP_200_OK, tags=['faqs'])
def list (
    page: int = Query(1, ge=1, description="Numero de pagina"),
    size: int = Query(10, ge=1, le=100, description="Preguntas frecuentes por pagina"),
    db: Session = Depends(get_db),
    faq_permission: Faq = Security(get_current_user, scopes=["view faqs"])
):
    try:
        params = Params(page=page, size=size)
        response = paginate(db.query(Faq), params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None
        return {
            "message": "Se ha obtenido la lista de preguntas frecuentes correctamente",
            "data": [FaqResponse.model_validate(faq) for faq in response.items],
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/faqs?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/faqs?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/faqs?page=1&size={size}",
                "last": f"/api/v1/faqs?page={response.pages}&size={size}"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de preguntas frecuentes {e}"
        )

@router.post(
    '/faqs',
    status_code=status.HTTP_201_CREATED,
    tags=['faqs']
)
def store (
        faq_store : FaqStore,
        db: Session = Depends(get_db),
        faq_permission: Faq = Security(get_current_user, scopes=["create faqs"])
):
    try:
        user = db.query(User).filter(User.id == faq_store.user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No eiste el usuario el cual desea asignar a esta pregunta frecuente"
            )
        category = db.query(Category).filter(Category.id == faq_store.category_id).first()
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la categoria el cual desea asignar a esta pregunta frecuente"
            )
        new_faq = Faq(**faq_store.model_dump())
        db.add(new_faq)
        db.commit()
        db.refresh(new_faq)
        return {
            "message": "Se ha registrado la pregunta frecuente correctamente",
            "data": FaqResponse.model_validate(new_faq)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la pregunta frecuente {e}"
        )

@router.get('/faqs/{id}', status_code=status.HTTP_200_OK, tags=['faqs'])
def show(
        id: int,
        db: Session = Depends(get_db),
        faq_permission: Faq = Security(get_current_user, scopes=["show faq"])
):
    try:
        faq = db.query(Faq).filter(Faq.id == id).first()
        if faq is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la pregunta frecuente que desea obtener"
            )
        return {
            "message": "Se ha obtenido la pregunte frecuente correctamente",
            "data": FaqResponse.model_validate(faq)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la pregunta frecuente {e}"
        )

@router.put('/faqs/{id}', status_code=status.HTTP_200_OK, tags=['faqs'])
def update(
        id: int,
        faq_update : FaqUpdate,
        db: Session = Depends(get_db),
        faq_permission: Faq = Security(get_current_user, scopes=["update faqs"])
):
    try:
        user = db.query(User).filter(User.id == faq_update.user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No eiste el usuario el cual desea asignar a esta pregunta frecuente"
            )
        category = db.query(Category).filter(Category.id == faq_update.category_id).first()
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la categoria el cual desea asignar a esta pregunta frecuente"
            )
        current_faq = db.query(Faq).filter(Faq.id == id).first()
        if current_faq is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la pregunta frecuente que desea actualizar"
            )
        faq_update.id = id
        for key, value in faq_update.model_dump(exclude_unset=True).items():
            setattr(current_faq, key, value)
        db.commit()
        db.refresh(current_faq)

        return {
            "message": "Se ha actualizado la pregunta frecuente correctamente",
            "data": FaqResponse.model_validate(current_faq)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la pregunta frecuente {e}"
        )


@router.delete('/faqs/{id}', status_code=status.HTTP_200_OK, tags=['faqs'])
def destroy(
        id: int,
        db: Session = Depends(get_db),
        faq_permission: Faq = Security(get_current_user, scopes=["delete faqs"])
):
    try:
        current_faq = db.query(Faq).filter(Faq.id == id).first()
        if current_faq is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la pregunta frecuente que desea eliminar"
            )
        db.delete(current_faq)
        db.commit()
        return {
            "message": "Se ha eliminado la pregunta frecuente correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la pregunta frecuente {e}"
        )