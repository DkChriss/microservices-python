import json

from fastapi import APIRouter, Depends, HTTPException, Query, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from services.security.schemas.user import UserResponse, UserStore, UserUpdate
from services.security.utils.dependency import  get_db
from services.security.models.user import User

import bcrypt

from services.security.utils.mapper import map_to_schema

router = APIRouter()

#CREAR NUEVO USUARIO
@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
)
def store(user: UserStore, db: Session = Depends(get_db)):
    try:
        hashed_password = bcrypt.hashpw(user.contraseña.encode("utf-8"), bcrypt.gensalt())
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
        print(id)
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
        return {
            "mensaje": "Se ha actualizado el usuario correctamente",
            "usuario": map_to_schema(user, UserStore)
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
        user.delete()
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