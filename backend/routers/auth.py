from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import verify_password, create_access_token, get_password_hash, get_current_user
from ..models.user import User
from ..schemas.schemas import Token, LoginRequest, UserCreate, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/token", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user

@router.post("/register-first-admin", response_model=UserOut)
def register_first_admin(data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = User(
            nome=data.nome,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            role="admin",
            cargo=data.cargo if data.cargo else None,
            matricula=None
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")

@router.post("/change-password")
def change_password(
    data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        senha_atual = data.get("senha_atual", "")
        nova_senha = data.get("nova_senha", "")
        if not senha_atual or not nova_senha:
            raise HTTPException(status_code=400, detail="Preencha todos os campos")
        if len(nova_senha) < 6:
            raise HTTPException(status_code=400, detail="Nova senha deve ter pelo menos 6 caracteres")
        if not verify_password(senha_atual, current_user.hashed_password):
            raise HTTPException(status_code=401, detail="Senha atual incorreta")
        current_user.hashed_password = get_password_hash(nova_senha)
        db.commit()
        return {"message": "Senha alterada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
