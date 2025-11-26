from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Esquema para recibir email y password
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Buscar usuario por email
    user = db.query(User).filter(User.email == data.email).first()

    # Si no existe o contraseña incorrecta → error estándar
    if not user or user.password != data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Devolver su información mínima (ej: user_id)
    return {
        "user_id": user.id,
        "email": user.email
    }
