from fastapi import APIRouter, status, Query, Depends, HTTPException, Security
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from services.security.models.category import Category
from services.security.schemas.category import CategoryResponse, CategoryStore, CategoryUpdate
from services.security.utils.dependency import  get_db
from services.security.utils.security import get_current_user

router = APIRouter()

@router.get('/categories', status_code=status.HTTP_200_OK, tags=['categories'])
def list (
    page: int = Query(1, ge=1, description="Numero de pagina"),
    size: int = Query(10, ge=1, le=100, description="Categorias por pagina"),
    db: Session = Depends(get_db),
    category_permission: Category = Security(get_current_user, scopes=["view categories"])
):
    try:
        params = Params(page=page, size=size)
        response = paginate(db.query(Category), params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None
        return {
            "message": "Se ha obtenido la lista de categorias correctamente",
            "data": [CategoryResponse.model_validate(category) for category in response.items],
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/categories?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/categories?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/categories?page=1&size={size}",
                "last": f"/api/v1/categories?page={response.pages}&size={size}"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de categorias {e}"
        )

@router.post(
    '/categories',
    status_code=status.HTTP_201_CREATED,
    tags=['categories']
)
def store (
        category_store : CategoryStore,
        db: Session = Depends(get_db),
        category_permission: Category = Security(get_current_user, scopes=["create categories"])
):
    try:
        new_category = Category(**category_store.model_dump())
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return {
            "message": "Se ha registrado la categoria correctamente",
            "data": CategoryResponse.model_validate(new_category)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la categoria {e}"
        )

@router.get('/categories/{id}', status_code=status.HTTP_200_OK, tags=['categories'])
def show(
        id: int,
        db: Session = Depends(get_db),
        category_permission: Category = Security(get_current_user, scopes=["show category"])
):
    try:
        category = db.query(Category).filter(Category.id == id).first()
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la categoria que desea obtener"
            )
        return {
            "message": "Se ha obtenido la categoria correctamente",
            "data": CategoryResponse.model_validate(category)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la categoria {e}"
        )

@router.put('/categories/{id}', status_code=status.HTTP_200_OK, tags=['categories'])
def update(
        id: int,
        category_update : CategoryUpdate,
        db: Session = Depends(get_db),
        category_permission: Category = Security(get_current_user, scopes=["update categories"])
):
    try:
        current_category = db.query(Category).filter(Category.id == id).first()
        if current_category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la categoria que desea actualizar"
            )
        category_update.id = id
        for key, value in category_update.model_dump(exclude_unset=True).items():
            setattr(current_category, key, value)
        db.commit()
        db.refresh(current_category)

        return {
            "message": "Se ha actualizado la categoria correctamente",
            "data": CategoryResponse.model_validate(current_category)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la categoria {e}"
        )


@router.delete('/categories/{id}', status_code=status.HTTP_200_OK, tags=['categories'])
def destroy(
        id: int,
        db: Session = Depends(get_db),
        category_permission: Category = Security(get_current_user, scopes=["delete categories"])
):
    try:
        current_category = db.query(Category).filter(Category.id == id).first()
        if current_category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la categoria que desea eliminar"
            )
        db.delete(current_category)
        db.commit()
        return {
            "message": "Se ha eliminado la categoria correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la categoria {e}"
        )