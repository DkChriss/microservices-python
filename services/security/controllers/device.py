from fastapi import APIRouter, status, Query, Depends, HTTPException, Security
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session, joinedload
from services.security.models.device import Device
from services.security.schemas.device import DeviceResponse, DeviceUpdate, DeviceStore
from services.security.utils.dependency import  get_db
from services.security.utils.security import get_current_user

router = APIRouter()

@router.get('/devices', status_code=status.HTTP_200_OK, tags=['devices'])
def list (
    page: int = Query(1, ge=1, description="Numero de pagina"),
    size: int = Query(10, ge=1, le=100, description="Dispositivos por pagina"),
    db: Session = Depends(get_db),
    device_permission: Device = Security(get_current_user, scopes=["view devices"])
):
    try:
        params = Params(page=page, size=size)
        query = db.query(Device).options(joinedload((Device.user)))
        response = paginate(query,params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None
        return {
            "message": "Se ha obtenido la lista de dispositivos correctamente",
            "data": [DeviceResponse.model_validate(device, from_attributes=True) for device in response.items],
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/devices?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/devices?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/devices?page=1&size={size}",
                "last": f"/api/v1/devices?page={response.pages}&size={size}"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de dispositivos {e}"
        )

@router.post(
    '/devices',
    status_code=status.HTTP_201_CREATED,
    tags=['devices']
)
def store (
        device_store : DeviceStore,
        db: Session = Depends(get_db),
        device_permission: Device = Security(get_current_user, scopes=["create devices"])
):
    try:
        new_device = Device(**device_store.model_dump())
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        return {
            "message": "Se ha registrado el dispositivo correctamente",
            "data": DeviceResponse.model_validate(new_device, from_attributes=True)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el dispositivo {e}"
        )

@router.get('/devices/{id}', status_code=status.HTTP_200_OK, tags=['devices'])
def show(
        id: int,
        db: Session = Depends(get_db),
        device_permission: Device = Security(get_current_user, scopes=["show device"])
):
    try:
        device = db.query(Device).filter(Device.id == id).first()
        if device is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el dispositivo que desea obtener"
            )
        return {
            "message": "Se ha obtenido el dispositivo correctamente",
            "data": DeviceResponse.model_validate(device, from_attributes=True)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el dispositivo {e}"
        )

@router.put('/devices/{id}', status_code=status.HTTP_200_OK, tags=['devices'])
def update(
        id: int,
        device_update : DeviceUpdate,
        db: Session = Depends(get_db),
        device_permission: Device = Security(get_current_user, scopes=["update devices"])
):
    try:
        current_device = db.query(Device).filter(Device.id == id).first()
        if current_device is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el dispositivo que desea actualizar"
            )
        device_update.id = id
        for key, value in device_update.model_dump(exclude_unset=True).items():
            setattr(current_device, key, value)
        db.commit()
        db.refresh(current_device)

        return {
            "message": "Se ha actualizado el dispositivo correctamente",
            "data": DeviceResponse.model_validate(current_device, from_attributes=True)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el dispositivo {e}"
        )


@router.delete('/devices/{id}', status_code=status.HTTP_200_OK, tags=['devices'])
def destroy(
        id: int,
        db: Session = Depends(get_db),
        device_permission: Device = Security(get_current_user, scopes=["delete devices"])
):
    try:
        current_device = db.query(Device).filter(Device.id == id).first()
        if current_device is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el dispositivo que desea eliminar"
            )
        db.delete(current_device)
        db.commit()
        return {
            "message": "Se ha eliminado la dispositivo correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la dispositivo {e}"
        )