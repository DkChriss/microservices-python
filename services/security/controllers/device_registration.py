from fastapi import APIRouter, status, Query, Depends, HTTPException, Security
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from services.security.models.device_registration import DeviceRegistration
from services.security.schemas.device_registration import DeviceRegistrationUpdate, DeviceRegistrationResponse, \
    DeviceRegistrationStore
from services.security.utils.dependency import  get_db
from services.security.utils.security import get_current_user

router = APIRouter()

@router.get('/devices-registration', status_code=status.HTTP_200_OK, tags=['devices-registration'])
def list (
    page: int = Query(1, ge=1, description="Numero de pagina"),
    size: int = Query(10, ge=1, le=100, description="Registro de dispositivos por pagina"),
    db: Session = Depends(get_db),
    device_registration: DeviceRegistration = Security(get_current_user, scopes=["view devices-registration"])
):
    try:
        params = Params(page=page, size=size)
        response = paginate(db.query(DeviceRegistration),params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None
        return {
            "message": "Se ha obtenido la lista de registro de dispositivos correctamente",
            "data": [DeviceRegistrationResponse.model_validate(device_registration) for device_registration in response.items],
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/devices-registration?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/devices-registration?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/devices-registration?page=1&size={size}",
                "last": f"/api/v1/devices-registration?page={response.pages}&size={size}"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de registro de dispositivos {e}"
        )

@router.post(
    '/devices-registration',
    status_code=status.HTTP_201_CREATED,
    tags=['devices-registration']
)
def store (
        device_registration_store : DeviceRegistrationStore,
        db: Session = Depends(get_db),
        device_registration_permission: DeviceRegistration = Security(get_current_user, scopes=["create devices-registration"])
):
    try:
        new_device_registration = DeviceRegistration(**device_registration_store.model_dump())
        db.add(new_device_registration)
        db.commit()
        db.refresh(new_device_registration)
        return {
            "message": "Se ha registrado el registro del dispositivo correctamente",
            "data": DeviceRegistrationResponse.model_validate(new_device_registration)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro del dispositivo {e}"
        )

@router.get('/devices-registration/{id}', status_code=status.HTTP_200_OK, tags=['devices-registration'])
def show(
        id: int,
        db: Session = Depends(get_db),
        device_registration_permission: DeviceRegistration = Security(get_current_user, scopes=["show device-registration"])
):
    try:
        device_registration = db.query(DeviceRegistration).filter(DeviceRegistration.id == id).first()
        if device_registration is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el registro del dispositivo que desea obtener"
            )
        return {
            "message": "Se ha obtenido el registro del dispositivo correctamente",
            "data": DeviceRegistrationResponse.model_validate(device_registration)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el registro del dispositivo {e}"
        )

@router.put('/devices-registration/{id}', status_code=status.HTTP_200_OK, tags=['devices-registration'])
def update(
        id: int,
        device_registration_update : DeviceRegistrationUpdate,
        db: Session = Depends(get_db),
        device_registration_permission: DeviceRegistration = Security(get_current_user, scopes=["update devices-registration"])
):
    try:
        current_device_registration = db.query(DeviceRegistration).filter(DeviceRegistration.id == id).first()
        if current_device_registration is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el dispositivo que desea actualizar"
            )
        device_registration_update.id = id
        for key, value in device_registration_update.model_dump(exclude_unset=True).items():
            setattr(current_device_registration, key, value)
        db.commit()
        db.refresh(current_device_registration)

        return {
            "message": "Se ha actualizado el registro de dispositio correctamente",
            "data": DeviceRegistrationResponse.model_validate(current_device_registration)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el registro de dispositivo {e}"
        )


@router.delete('/devices-registration/{id}', status_code=status.HTTP_200_OK, tags=['devices-registration'])
def destroy(
        id: int,
        db: Session = Depends(get_db),
        device_registration_permission: DeviceRegistration = Security(get_current_user, scopes=["delete devices-registration"])
):
    try:
        current_device = db.query(DeviceRegistration).filter(DeviceRegistration.id == id).first()
        if current_device is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el registro de dispositivo que desea eliminar"
            )
        db.delete(current_device)
        db.commit()
        return {
            "message": "Se ha eliminado el registro de dispositivo correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el registro de dispositivo {e}"
        )