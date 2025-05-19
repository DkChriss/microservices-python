from fastapi import APIRouter, status, Query, Depends, HTTPException, Security
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from services.security.models.emergency_contact import EmergencyContact
from services.security.schemas.emergency_contact import EmergencyContactResponse, EmergencyContactUpdate, \
    EmergencyContactStore
from services.security.utils.dependency import  get_db
from services.security.utils.security import get_current_user

router = APIRouter()

@router.get(
    '/emergency-contacts',
    status_code=status.HTTP_200_OK,
    tags=['emergency-contacts']
)
def list (
    page: int = Query(1, ge=1, description="Numero de pagina"),
    size: int = Query(10, ge=1, le=100, description="Contactos de emergencia por pagina"),
    db: Session = Depends(get_db),
    emergency_contact_permission: EmergencyContact = Security(get_current_user, scopes=["view emergency-contacts"])
):
    try:
        params = Params(page=page, size=size)
        response = paginate(db.query(EmergencyContact),params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None
        return {
            "message": "Se ha obtenido la lista de contactos de emergencia correctamente",
            "data": [EmergencyContactResponse.model_validate(emergency_contact) for emergency_contact in response.items],
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/emergency-contacts?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/emergency-contacts?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/emergency-contacts?page=1&size={size}",
                "last": f"/api/v1/emergency-contacts?page={response.pages}&size={size}"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de contactos de emergencia {e}"
        )

@router.post(
    '/emergency-contacts',
    status_code=status.HTTP_201_CREATED,
    tags=['emergency-contacts']
)
def store (
        emergency_contact_store : EmergencyContactStore,
        db: Session = Depends(get_db),
        emergency_contact_permission: EmergencyContact = Security(get_current_user, scopes=["create emergency-contacts"])
):
    try:
        new_emergency_contact = EmergencyContact(**emergency_contact_store.model_dump())
        db.add(new_emergency_contact)
        db.commit()
        db.refresh(new_emergency_contact)
        return {
            "message": "Se ha registrado el contacto de emergencia correctamente",
            "data": EmergencyContactResponse.model_validate(new_emergency_contact)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el contacto de emergencia {e}"
        )

@router.get(
    '/emergency-contacts/{id}',
    status_code=status.HTTP_200_OK,
    tags=['emergency-contacts']
)
def show(
        id: int,
        db: Session = Depends(get_db),
        emergency_contact_permission: EmergencyContact = Security(get_current_user, scopes=["show emergency-contact"])
):
    try:
        emergency_contact = db.query(EmergencyContact).filter(EmergencyContact.id == id).first()
        if emergency_contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el contacto de emergencia que desea obtener"
            )
        return {
            "message": "Se ha obtenido el contacto de emergencia correctamente",
            "data": EmergencyContactResponse.model_validate(emergency_contact)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el contacto de emergencia {e}"
        )

@router.put(
    '/emergency-contacts/{id}',
    status_code=status.HTTP_200_OK,
    tags=['emergency-contacts']
)
def update(
        id: int,
        emergency_contact_update : EmergencyContactUpdate,
        db: Session = Depends(get_db),
        emergency_contact_permission: EmergencyContact = Security(get_current_user, scopes=["update emergency-contacts"])
):
    try:
        current_emergency_contact = db.query(EmergencyContact).filter(EmergencyContact.id == id).first()
        if current_emergency_contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el contacto de emergencia que desea actualizar"
            )
        emergency_contact_update.id = id
        for key, value in emergency_contact_update.model_dump(exclude_unset=True).items():
            setattr(current_emergency_contact, key, value)
        db.commit()
        db.refresh(current_emergency_contact)

        return {
            "message": "Se ha actualizado el contacto de emergencia correctamente",
            "data": EmergencyContactResponse.model_validate(current_emergency_contact)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el contacto de emergencia {e}"
        )


@router.delete(
    '/emergency-contacts/{id}',
    status_code=status.HTTP_200_OK,
    tags=['emergency-contacts']
)
def destroy(
        id: int,
        db: Session = Depends(get_db),
        emergency_contact_permission: EmergencyContact = Security(get_current_user, scopes=["delete emergency-contacts"])
):
    try:
        current_emergency_contact = db.query(EmergencyContact).filter(EmergencyContact.id == id).first()
        if current_emergency_contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el contacto de emergencia que desea eliminar"
            )
        db.delete(current_emergency_contact)
        db.commit()
        return {
            "message": "Se ha eliminado el contacto de emergencia correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el contacto de emergencia {e}"
        )