import json

from fastapi import APIRouter, Depends, HTTPException, Query, Form, status
from fastapi_pagination import paginate, Params
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from services.security.schemas.user import UserResponse, UserStore, UserUpdate
from services.security.utils.dependency import  get_db
from services.security.models.user import User
from services.security.utils.mapper import map_to_schema

router = APIRouter()
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

@router.get("/users", status_code=status.HTTP_200_OK)
def lista(
        page: int = Query(1, ge=1, description="Numero de pagina"),
        size: int = Query(10, ge=1, le=100, description="Usuarios por pagina"),
        db: Session = Depends(get_db)
):
    try:
        params = Params(page=page, size=size)
        query = db.query(User)
        response = paginate(query.all(), params)

        next_page = page + 1 if page * size < response.total else None
        prev_page = page - 1 if page > 1 else None

        return {
            "mensaje": "Se ha obtenido la lista de usuarios correctamente",
            "lista": response.items,
            "total": response.total,
            "pagina": response.page,
            "tamaño": response.size,
            "links": {
                "siguiente": f"/api/v1/users?page={next_page}&size={size}" if next_page else None,
                "anterior": f"/api/v1/users?page={prev_page}&size={size}" if prev_page else None,
                "primera": f"/api/v1/users?page=1&size={size}",
                "ultima": f"/api/v1/users?page={response.pages}&size={size}"
            }
        }
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la lista de usuarios: {str(e)}"
        )
#CREAR NUEVO USUARIO
@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
)
def store(user: UserStore, db: Session = Depends(get_db)):
    try:
        hashed_password = bcrypt_context.hash(user.contraseña)
        user.contraseña = hashed_password
        newUser = User(**user.dict())
        db.add(newUser)
        db.commit()
        db.refresh(newUser)

        return {
            "mensaje": "Se ha registrado el usuario correctamente",
            "usuario": newUser
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al registrar el usuario: {e}"
        )

#OBTENER EL USUARIO
@router.get(
    "/users/{id}",
    tags=["users"]
)
def show(id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el usuario con que desea obtener"
            )

        return {
            "mensaje": "Se ha obtenido el usuario correctamente",
            "usuario": user
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al registrar el usuario: {e}"
        )

#ACTUALIZAR USUARIO
@router.put(
    "/users/{id}",
    status_code=status.HTTP_200_OK,
    tags=["users"]
)
def update(id: int ,userUpdate: UserUpdate, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el usuario que desea actualizar"
            )
        for key, value in userUpdate.dict(exclude_unset=True).items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        response = map_to_schema(user, UserStore)
        return {
            "mensaje": "Se ha actualizado el usuario correctamente",
            "usuario": response
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al actualizar el usuario: {e}"
        )

#ELIMINAR USUARIO
@router.delete(
    "/users/{id}",
    tags=["users"]
)
def destroy(id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el usuario que desea eliminar"
            )
        db.delete(user)
        db.commit()
        return {
            "mensaje": "Se ha eliminado el usuario correctamente"
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al eliminar el usuario: {e}"
        )