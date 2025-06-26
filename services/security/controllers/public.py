from fastapi import APIRouter, Depends, HTTPException, status
from services.security.schemas.report import ReportResponse, ReportStore
from services.security.utils.dependency import  get_db
from sqlalchemy.orm import Session
from services.security.schemas.report import ReportStore
from services.security.models.report import Report

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