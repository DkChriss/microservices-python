import os

from fastapi import APIRouter, Depends, HTTPException, Query, status, Security, Form, UploadFile, File
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from models.report import Report
from models.report_has_files import ReportHasFiles
from utils.dependency import  get_db
from utils.security import get_current_user
from utils.files import save_image_file
from schemas.report import ReportResponse, ReportStore, ReportUpdate

router = APIRouter()
@router.get(
    "/reports",
    status_code=status.HTTP_200_OK,
    tags=["reports"]
)
def list(
        page: int = Query(1, ge=1, description="Numero de pagina"),
        size: int = Query(10, ge=1, le=100, description="Reportes por pagina"),
        search: str = Query("",description="Buscar reporte"),
        db: Session = Depends(get_db),
        report_permission: Report = Security(get_current_user, scopes=["view reports"])
):
    try:
        params = Params(page=page, size=size)
        query = db.query(Report)
        if search:
            query = query.filter(
                or_(
                    Report.name.like(f'%{search}%'),
                    Report.phone.like(f'%{search}%'),
                    Report.email.like(f'%{search}%'),
                    Report.location.like(f'%{search}%'),
                    Report.description.like(f'%{search}%'),
                    Report.date.like(f'%{search}%'),
                )
            )
        response = paginate(query, params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None

        return {
            "message": "Se ha obtenido la lista de reportes correctamente",
            "data": [ReportResponse.model_validate(report) for report in response.items],
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/reports?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/reports?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/reports?page=1&size={size}",
                "last": f"/api/v1/reports?page={response.pages}&size={size}"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de reportes: {str(e)}"
        )

@router.post(
    "/reports",
    status_code=status.HTTP_201_CREATED,
    tags=["reports"]
)
def store(
        report_store: ReportStore,
        report_file: UploadFile = File(...),
        db: Session = Depends(get_db),
        report_permission: Report = Security(get_current_user, scopes=["create reports"])
):

    try:
        new_report = Report(**report_store.model_dump())
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        relative_photo_path = save_image_file(report_file, f"reporte_de_{report_store.name}", report_store.missing_id, "reports")
        saved_photo_path = os.path.join(relative_photo_path)
        new_report_file = ReportHasFiles(
            report_id = new_report.id,
            path = saved_photo_path,
            name = f"reporte_de_{report_store.name}",
        )
        db.add(new_report_file)
        db.commit()
        db.refresh(new_report_file)
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

@router.get('/reports/{id}', status_code=status.HTTP_200_OK, tags=['reports'])
def show(
        id: int,
        db: Session = Depends(get_db),
        report_permission: Report = Security(get_current_user, scopes=["show report"])
):
    try:
        report = db.query(Report).options(
            joinedload(Report.missing)
        ).filter(Report.id == id).first()
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el reporte que desea obtener"
            )
        return {
            "message": "Se ha obtenido el reporte correctamente",
            "data": ReportResponse.model_validate(report, from_attributes=True)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el reporte {e}"
        )

@router.put('/reports/{id}', status_code=status.HTTP_200_OK, tags=['reports'])
def update(
        id: int,
        report_update : ReportUpdate,
        report_file: UploadFile = File(...),
        db: Session = Depends(get_db),
        report_permission: Report = Security(get_current_user, scopes=["update reports"])
):
    try:
        current_report = db.query(Report).filter(Report.id == id).first()
        if current_report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el reporte que desea actualizar"
            )
        report_update.id = id
        for key, value in report_update.model_dump(exclude_unset=True).items():
            setattr(current_report, key, value)
        db.commit()
        db.refresh(current_report)
        relative_photo_path = save_image_file(report_file, f"reporte_de_{current_report.name}", current_report.missing_id, "reports")
        saved_photo_path = os.path.join(relative_photo_path)
        new_report_file = ReportHasFiles(
            report_id = current_report.id,
            path = saved_photo_path,
            name = f"reporte_de_{current_report.name}",
        )
        db.add(new_report_file)
        db.commit()
        db.refresh(new_report_file)
        return {
            "message": "Se ha actualizado el reporte correctamente",
            "data": ReportResponse.model_validate(current_report, from_attributes=True)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el reporte {e}"
        )

@router.delete('/reports/{id}', status_code=status.HTTP_200_OK, tags=['reports'])
def destroy(
        id: int,
        db: Session = Depends(get_db),
        report_permission: Report = Security(get_current_user, scopes=["delete reports"])
):
    try:
        current_report = db.query(Report).filter(Report.id == id).first()
        if current_report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el reporte que desea eliminar"
            )
        db.delete(current_report)
        db.commit()
        return {
            "message": "Se ha eliminado el reporte correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el reporte {e}"
        )