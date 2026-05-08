from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..core.security import get_current_user, require_admin, get_password_hash
from ..models.user import User
from ..schemas.schemas import UserCreate, UserUpdate, UserOut
from ..services.email_service import send_welcome_email
import secrets

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(User).filter(User.is_active == True).all()

@router.post("/", response_model=UserOut)
def create_user(data: UserCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    user = User(
        nome=data.nome,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=data.role,
        especialidade=data.especialidade,
        cargo=data.cargo,
        telefone=data.telefone,
        matricula=data.matricula
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    send_welcome_email(user.email, user.nome)
    return user

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if current_user.role not in ("admin", "gestor") and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def deactivate_user(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.is_active = False
    db.commit()
    return {"message": "Usuário desativado"}
