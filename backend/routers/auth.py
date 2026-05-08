from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import verify_password, create_access_token, get_password_hash, get_current_user
from ..models.user import User
from ..schemas.schemas import Token, LoginRequest, UserCreate, UserOut
from ..services.email_service import send_welcome_email

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/token", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuário inativo")
    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "nome": user.nome, "email": user.email, "role": user.role}
    }

@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user

@router.post("/register-first-admin", response_model=UserOut)
def register_first_admin(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).count() > 0:
        raise HTTPException(status_code=400, detail="Já existe usuário cadastrado. Use o painel de administração.")
    user = User(
        nome=data.nome,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role="admin",
        cargo=data.cargo,
        matricula=data.matricula
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
