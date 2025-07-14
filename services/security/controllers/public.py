from fastapi import APIRouter, status, Query, Depends, HTTPException, Form, Security, UploadFile, File
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import or_, and_
from services.security.models.category import Category
from services.security.models.contact_support import ContactSupport
from services.security.models.guide import Guide
from services.security.models.missing import Missing
from services.security.models.report_has_files import ReportHasFiles
from services.security.schemas.contact_support import ContactSupportStore, ContactSupportResponse
from services.security.schemas.guide import GuideResponse
from services.security.schemas.report import ReportResponse
from services.security.utils.dependency import  get_db
from sqlalchemy.orm import Session, selectinload
from services.security.schemas.report import ReportStore
from services.security.models.report import Report
from services.security.utils.files import save_image_file
from services.security.schemas.missing import MissingResponse
from services.security.models.status_missing import StatusMissingEnum
from datetime import date
import os
import base64
import mimetypes
router = APIRouter()

@router.post(
    "/reports",
    status_code=status.HTTP_201_CREATED
)
def storeReport(
        report_store: ReportStore,
        report_file: UploadFile = File(...),
        db: Session = Depends(get_db),
):
    try:
        new_report = Report(**report_store.model_dump())
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        relative_photo_path = save_image_file(report_file, f"reporte_de_{report_store.name}", report_store.missing_id, "reports")
        saved_photo_path = os.path.join("services", "security", relative_photo_path)
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
def listMissing (
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
                and_(
                    or_(
                        Missing.name.like(f'%{search}%'),
                        Missing.last_name.like(f'%{search}%'),
                        Missing.reporter_phone.like(f'%{search}%'),
                    ),
                    Missing.status_missing == "progress"
                )
            )
        else:
            query = query.filter(
                and_(
                    Missing.status_missing == "progress"
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

@router.post(
    '/missing',
    status_code=status.HTTP_201_CREATED,
)
def storeMissing (
        name: str = Form(...),
        last_name: str = Form(...),
        age: int = Form(...),
        gender: str = Form(...),
        description: str = Form(...),
        birthdate: date = Form(...),
        disappearance_date: date = Form(...),
        place_of_disappearance: str = Form(...),
        photo: UploadFile = File(...),
        characteristics: str = Form(...),
        reporter_name: str = Form(...),
        reporter_phone: int = Form(...),
        event_photo: UploadFile = File(...),
        db: Session = Depends(get_db),
):
    saved_photo_path = None
    saved_event_photo_path = None

    try:
        relative_photo_path = save_image_file(photo, f"perfil_{name}", last_name, disappearance_date, "missing")
        saved_photo_path = os.path.join("services", "security", relative_photo_path)

        relative_photo_event_path = save_image_file(event_photo, f"evento_{name}", last_name, disappearance_date, "missing")
        saved_event_photo_path = os.path.join("services", "security", relative_photo_event_path)

        new_missing = Missing(
            name=name,
            last_name=last_name,
            age=age,
            gender=gender,
            description=description,
            birthdate=birthdate,
            disappearance_date=disappearance_date,
            place_of_disappearance=place_of_disappearance,
            status_missing=StatusMissingEnum.pending,
            photo=relative_photo_path,
            characteristics=characteristics,
            reporter_name=reporter_name,
            reporter_phone=reporter_phone,
            event_photo=relative_photo_event_path,
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

@router.get('/list-category-faqs', status_code=status.HTTP_200_OK)
def list_category_faqs(
        page: int = Query(1, ge=1, description="Número de página"),
        size: int = Query(10, ge=1, le=100, description="Categorías por página"),
        db: Session = Depends(get_db)
):
    try:
        params = Params(page=page, size=size)
        query = db.query(Category).options(selectinload(Category.faqs))
        response = paginate(query, params)
        result = []
        for category in response.items:
            if category.faqs:
                result.append({
                    "id": category.id,
                    "title": category.title,
                    "faqs": [{"id": faq.id, "question": faq.question, "answer": faq.answer} for faq in category.faqs]
                })
        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None

        return {
            "message": "Se ha obtenido la lista de categorías con FAQs correctamente",
            "data": result,
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/public/list-category-faqs?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/public/list-category-faqs?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/public/list-category-faqs?page=1&size={size}",
                "last": f"/api/v1/public/list-category-faqs?page={response.pages}&size={size}"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de preguntas: {e}"
        )

@router.get('/list-category-guides', status_code=status.HTTP_200_OK)
def list_category_guides(
        page: int = Query(1, ge=1, description="Número de página"),
        size: int = Query(10, ge=1, le=100, description="Categorías por página"),
        db: Session = Depends(get_db)
):
    try:
        params = Params(page=page, size=size)
        query = db.query(Category).options(selectinload(Category.guides))
        response = paginate(query, params)
        result = []
        for category in response.items:
            if category.guides:
                result.append({
                    "id": category.id,
                    "title": category.title,
                    "guides": [{"id": guide.id, "title": guide.title} for guide in category.guides]
                })

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None

        return {
            "message": "Se ha obtenido la lista de categorías con guias correctamente",
            "data": result,
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/public/list-category-guides?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/public/list-category-guides?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/public/list-category-guides?page=1&size={size}",
                "last": f"/api/v1/public/list-category-guides?page={response.pages}&size={size}"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de guias: {e}"
        )

@router.get('/list-guides', status_code=status.HTTP_200_OK)
def list_guides(
        page: int = Query(1, ge=1, description="Numero de pagina"),
        size: int = Query(10, ge=1, le=100, description="Guias por pagina"),
        search: str = Query("", description="Buscar guia"),
        db: Session = Depends(get_db)
):
    try:
        params = Params(page=page, size=size)
        query = db.query(Guide)
        if search:
            query = query.filter(
                or_(
                    Guide.title.like(f'%{search}%'),
                    Guide.slug.like(f'%{search}%'),
                    Guide.subtitle.like(f'%{search}%'),
                    Guide.content.like(f'%{search}%'),
                )
            )
        response = paginate(query, params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None
        return {
            "message": "Se ha obtenido la lista de guias correctamente",
            "data": [GuideResponse.model_validate(guide, from_attributes=True) for guide in response.items],
            "total": response.total,
            "page": response.page,
            "size": response.size,
            "links": {
                "next": f"/api/v1/public/list-guides?page={next_page}&size={size}" if next_page else None,
                "previous": f"/api/v1/public/list-guides?page={prev_page}&size={size}" if prev_page else None,
                "first": f"/api/v1/public/list-guides?page=1&size={size}",
                "last": f"/api/v1/public/list-guides?page={response.pages}&size={size}"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de guias {e}"
        )

@router.post('/contact-support', status_code=status.HTTP_201_CREATED)
def storeContactSupport(
        contactSupportStore: ContactSupportStore,
        db: Session = Depends(get_db),
):
    try:
        new_contact_support = ContactSupport(**contactSupportStore.model_dump())
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