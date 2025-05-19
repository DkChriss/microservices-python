from fastapi import APIRouter, status, Query, Depends, HTTPException, Security
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from services.security.models.contact_support import ContactSupport
from services.security.schemas.contact_support import ContactSupportResponse, ContactSupportUpdate, ContactSupportStore
from services.security.utils.dependency import  get_db
from services.security.utils.security import get_current_user

router = APIRouter()

@router.get('/contacts-support', status_code=status.HTTP_200_OK, tags=['contacts-support'])
def list (
    page: int = Query(1, ge=1, description="Numero de pagina"),
    size: int = Query(10, ge=1, le=100, description="Contactos de soporte por pagina"),
    db: Session = Depends(get_db),
    contact_support: ContactSupport = Security(get_current_user, scopes=["view contacts-support"])
):
    try:
        params = Params(page=page, size=size)
        response = paginate(db.query(ContactSupport), params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None
        return {
            "message": "Se ha obtenido la lista de contactos de soporte correctamente",
            "data": [ContactSupportResponse.model_validate(contact_support) for contact_support in response.items],
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/contacts-support?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/contacts-support?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/contacts-support?page=1&size={size}",
                "last": f"/api/v1/contacts-support?page={response.pages}&size={size}"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de contactos del soporte {e}"
        )

@router.post(
    '/contacts-support',
    status_code=status.HTTP_201_CREATED,
    tags=['contacts-support']
)
def store (
        contact_support_store : ContactSupportStore,
        db: Session = Depends(get_db),
        contact_support: ContactSupport = Security(get_current_user, scopes=["create contacts-support"])
):
    try:
        new_contact_support = ContactSupport(**contact_support_store.model_dump())
        db.add(new_contact_support)
        db.commit()
        db.refresh(new_contact_support)
        return {
            "message": "Se ha registrado el contacto de soporte correctamente",
            "data": ContactSupportResponse.model_validate(new_contact_support)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el contacto del soporte {e}"
        )

@router.get('/contacts-support/{id}', status_code=status.HTTP_200_OK, tags=['contacts-support'])
def show(
        id: int,
        db: Session = Depends(get_db),
        contact_support: ContactSupport = Security(get_current_user, scopes=["show contact-support"])
):
    try:
        contact_support = db.query(ContactSupport).filter(ContactSupport.id == id).first()
        if contact_support is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el contacto de soporte que desea obtener"
            )
        return {
            "message": "Se ha obtenido el contacto de soporte correctamente",
            "data": ContactSupportResponse.model_validate(contact_support)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el contacto de soporte {e}"
        )

@router.put('/contacts-support/{id}', status_code=status.HTTP_200_OK, tags=['contacts-support'])
def update(
        id: int,
        contact_support_update : ContactSupportUpdate,
        db: Session = Depends(get_db),
        contact_support: ContactSupport = Security(get_current_user, scopes=["update contacts-support"])
):
    try:
        current_contact_support = db.query(ContactSupport).filter(ContactSupport.id == id).first()
        if current_contact_support is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el contacto de soporte que desea actualizar"
            )
        contact_support_update.id = id
        for key, value in contact_support_update.model_dump(exclude_unset=True).items():
            setattr(current_contact_support, key, value)
        db.commit()
        db.refresh(current_contact_support)

        return {
            "message": "Se ha actualizado el contacto de soporte correctamente",
            "data": ContactSupportResponse.model_validate(current_contact_support)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la el contacto de soporte {e}"
        )


@router.delete('/contacts-support/{id}', status_code=status.HTTP_200_OK, tags=['contacts-support'])
def destroy(
        id: int,
        db: Session = Depends(get_db),
        contact_support: ContactSupport = Security(get_current_user, scopes=["delete contacts-support"])
):
    try:
        current_contact_support = db.query(ContactSupport).filter(ContactSupport.id == id).first()
        if current_contact_support is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el contacto de soporte que desea eliminar"
            )
        db.delete(current_contact_support)
        db.commit()
        return {
            "message": "Se ha eliminado el contacto de soporte correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el contacto de soporte {e}"
        )