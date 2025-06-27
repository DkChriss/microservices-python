from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import or_
from services.security.models.missing import Missing
from services.security.schemas.missing import MissingResponse
from services.security.schemas.report import ReportResponse
from services.security.utils.dependency import  get_db
from sqlalchemy.orm import Session
from services.security.schemas.report import ReportStore
from services.security.models.report import Report
import os
import base64
import mimetypes
router = APIRouter()

@router.post(
    "/reports",
    status_code=status.HTTP_201_CREATED
)
def store(
        report_store: ReportStore,
        db: Session = Depends(get_db),
):
    try:
        new_report = Report(**report_store.model_dump())
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        return {
            "message": "Se ha registrado el reporte correctamente",
            "data": ReportResponse.model_validate(new_report)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al registrar el reporte: {e}"
        )
def encode_image(path: str) -> str:
    if not os.path.exists(path):
        return None
    mime_type, _ = mimetypes.guess_type(path)
    with open(path, "rb") as f:
        return f"data:{mime_type};base64," + base64.b64encode(f.read()).decode("utf-8")
@router.get(
    '/missing',
    status_code=status.HTTP_200_OK,
)
def list (
    page: int = Query(1, ge=1, description="Numero de pagina"),
    size: int = Query(10, ge=1, le=100, description="Solicitudes de desaparecidos por pagina"),
    search: str = Query("",description="Buscar solicitud de desaparecidos"),
    db: Session = Depends(get_db),
):
    try:
        params = Params(page=page, size=size)
        query = db.query(Missing)

        if search:
            query = query.filter(
                or_(
                    Missing.name.like(f'%{search}%'),
                    Missing.last_name.like(f'%{search}%'),
                    Missing.status_missing.like(f'%{search}%'),
                    Missing.reporter_phone.like(f'%{search}%')
                )
            )
        response = paginate(query,params)
        result = []
        for missing in response.items:
            photo_path = os.path.join("services", "security", missing.event_photo)

            result.append({
                "id": missing.id,
                "name": missing.name,
                "last_name": missing.last_name,
                "gender": missing.gender,
                "age": missing.age,
                "description": missing.description,
                "characteristics": missing.characteristics,
                "place_of_disappearance": missing.place_of_disappearance,
                "photo": encode_image(photo_path),
            })
        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None
        return {
            "message": "Se ha obtenido la lista de solicitudes de desaparecido correctamente",
            "data": result,
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/public/missing?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/public/missing?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/public/missing?page=1&size={size}",
                "last": f"/api/v1/public/missing?page={response.pages}&size={size}"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de solicitudes de desaparecidos {e}"
        )