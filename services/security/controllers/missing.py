import json
import os
from datetime import date
from typing import Dict, Any
from fastapi import APIRouter, status, Query, Depends, HTTPException, Form, Security, UploadFile, File
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from services.security.models.missing import Missing
from services.security.models.status_missing import StatusMissingEnum
from services.security.schemas.missing import MissingResponse, MissingUpdate
from services.security.utils.dependency import  get_db
from services.security.utils.files import save_image_file
from services.security.utils.security import get_current_user

router = APIRouter()

@router.get(
    '/missing',
    status_code=status.HTTP_200_OK,
    tags=['missing']
)
def list (
    page: int = Query(1, ge=1, description="Numero de pagina"),
    size: int = Query(10, ge=1, le=100, description="Solicitudes de desaparecidos por pagina"),
    db: Session = Depends(get_db),
    missing_permission: Missing = Security(get_current_user, scopes=["view missing"])
):
    try:
        params = Params(page=page, size=size)
        response = paginate(db.query(Missing),params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None
        return {
            "message": "Se ha obtenido la lista de solicitudes de desaparecido correctamente",
            "data": [MissingResponse.model_validate(missing) for missing in response.items],
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/missing?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/missing?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/missing?page=1&size={size}",
                "last": f"/api/v1/missing?page={response.pages}&size={size}"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de solicitudes de desaparecidos {e}"
        )

@router.post(
    '/missing',
    status_code=status.HTTP_201_CREATED,
    tags=['misiing']
)
def store (
        user_id: int = Form(...),
        name: str = Form(...),
        last_name: str = Form(...),
        age: int = Form(...),
        gender: str = Form(...),
        description: str = Form(...),
        birthdate: date = Form(...),
        disappearance_date: date = Form(...),
        place_of_disappearance: str = Form(...),
        status_missing: StatusMissingEnum = Form(...),
        photo: UploadFile = File(...),
        characteristics: str = Form(...),
        reporter_name: str = Form(...),
        reporter_phone: int = Form(...),
        event_photo: UploadFile = File(...),
        location: str = Form(...),
        db: Session = Depends(get_db),
        missing_permission: Missing = Security(get_current_user, scopes=["create missing"])
):
    saved_photo_path = None
    saved_event_photo_path = None

    try:
        relative_photo_path = save_image_file(photo, f"perfil_{name}", last_name, disappearance_date, "missing")
        saved_photo_path = os.path.join("services", "security", relative_photo_path)

        relative_photo_event_path = save_image_file(event_photo, f"evento_{name}", last_name, disappearance_date, "missing")
        saved_event_photo_path = os.path.join("services", "security", relative_photo_event_path)

        new_missing = Missing(
            user_id=user_id,
            name=name,
            last_name=last_name,
            age=age,
            gender=gender,
            description=description,
            birthdate=birthdate,
            disappearance_date=disappearance_date,
            place_of_disappearance=place_of_disappearance,
            status_missing=status_missing,
            photo=relative_photo_path,
            characteristics=characteristics,
            reporter_name=reporter_name,
            reporter_phone=reporter_phone,
            event_photo=relative_photo_event_path,
            location=json.loads(location)
        )
        db.add(new_missing)
        db.commit()
        db.refresh(new_missing)
        return {
            "message": "Se ha registrado la solicitud de desaparecido correctamente",
            "data": MissingResponse.model_validate(new_missing)
        }
    except Exception as e:
        db.rollback()
        if saved_photo_path and os.path.exists(saved_photo_path):
            os.remove(saved_photo_path)
        if saved_event_photo_path and os.path.exists(saved_event_photo_path):
            os.remove(saved_event_photo_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la solicitud de desaparecido {e}"
        )

@router.get(
    '/missing/{id}',
    status_code=status.HTTP_200_OK,
    tags=['missing']
)
def show(
        id: int,
        db: Session = Depends(get_db),
        missing_permission: Missing = Security(get_current_user, scopes=["show missing"])
):
    try:
        missing = db.query(Missing).filter(Missing.id == id).first()
        if missing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la solicitud de desaparecido que desea obtener"
            )
        return {
            "message": "Se ha obtenido la solicitud de desaparecido correctamente",
            "data": MissingResponse.model_validate(missing)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la solicitud de desaparecido {e}"
        )

@router.put(
    '/missing/{id}',
    status_code=status.HTTP_200_OK,
    tags=['missing']
)
def update(
        id: int,
        user_id: int = Form(...),
        name: str = Form(...),
        last_name: str = Form(...),
        age: int = Form(...),
        gender: str = Form(...),
        description: str = Form(...),
        birthdate: date = Form(...),
        disappearance_date: date = Form(...),
        place_of_disappearance: str = Form(...),
        status_missing: StatusMissingEnum = Form(...),
        photo: UploadFile = File(None),
        characteristics: str = Form(...),
        reporter_name: str = Form(...),
        reporter_phone: int = Form(...),
        event_photo: UploadFile = File(None),
        location: str = Form(...),
        db: Session = Depends(get_db),
        missing_permission: Missing = Security(get_current_user, scopes=["update missing"])
):
    new_photo_path = None
    new_event_photo_path = None
    try:
        current_missing = db.query(Missing).filter(Missing.id == id).first()
        if current_missing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la solicitud de desaparecido que desea actualizar"
            )
        if photo:
            new_relative_photo_path = save_image_file(photo, f"perfil_{name}", last_name, disappearance_date, "missing")
            new_photo_path = os.path.join("services", "security", new_relative_photo_path)

            old_photo_path = os.path.join("services", "security", current_missing.photo)
            if os.path.exists(old_photo_path) and old_photo_path != new_photo_path:
                os.remove(old_photo_path)
            current_missing.photo = new_photo_path

        if event_photo:
            new_relative_event_photo_path = save_image_file(photo, f"evento_{name}", last_name, disappearance_date, "missing")
            new_event_photo_path = os.path.join("services", "security", new_relative_event_photo_path)

            old_event_photo_path = os.path.join("services", "security", current_missing.event_photo)
            if os.path.exists(old_event_photo_path) and old_event_photo_path != new_photo_path:
                os.remove(old_event_photo_path)
            current_missing.event_photo = new_event_photo_path

        #UPDATE OTHER FIELDS
        current_missing.user_id = user_id
        current_missing.name = name
        current_missing.last_name = last_name
        current_missing.age = age
        current_missing.gender = gender
        current_missing.description = description
        current_missing.birthdate = birthdate
        current_missing.disappearance_date = disappearance_date
        current_missing.place_of_disappearance = place_of_disappearance
        current_missing.status_missing = status_missing
        current_missing.characteristics = characteristics
        current_missing.reporter_name = reporter_name
        current_missing.reporter_phone = reporter_phone
        current_missing.location = json.loads(location)
        db.commit()
        db.refresh(current_missing)

        return {
            "message": "Se ha actualizado la solicitud de desaparecido",
            "data": MissingResponse.model_validate(current_missing)
        }

    except Exception as e:
        db.rollback()
        if new_photo_path and os.path.exists(new_photo_path):
            os.remove(new_photo_path)
        if new_event_photo_path and os.path.exists(new_event_photo_path):
            os.remove(new_event_photo_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la solicitud de desaparecido {e}"
        )


@router.delete(
    '/missing/{id}',
    status_code=status.HTTP_200_OK,
    tags=['missing']
)
def destroy(
        id: int,
        db: Session = Depends(get_db),
        missing_permission: Missing = Security(get_current_user, scopes=["delete missing"])
):
    try:
        missing = db.query(Missing).filter(Missing.id == id).first()
        if missing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe la solicitud de desaparecido que desea eliminar"
            )
        db.delete(missing)
        db.commit()
        photo_path = os.path.join("services", "security", missing.photo)
        if os.path.exists(photo_path):
            os.remove(photo_path)
        event_photo_path = os.path.join("services","security", missing.event_photo)
        if os.path.exists(event_photo_path):
            os.remove(event_photo_path)
        return {
            "message": "Se ha eliminado la solicitud de desaparecido correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la solicitud de desaparecido {e}"
        )