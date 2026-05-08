from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import PlanoPreventiva, User
from ..schemas.schemas import PlanoCreate, PlanoUpdate, PlanoOut

router = APIRouter(prefix="/api/preventivas", tags=["preventivas"])

def _enrich(p: PlanoPreventiva) -> dict:
    d = {c.name: getattr(p, c.name) for c in p.__table__.columns}
    d["equipamento_nome"] = p.equipamento_rel.nome if p.equipamento_rel else None
    d["responsavel_nome"] = p.responsavel_rel.nome if p.responsavel_rel else None
    return d

@router.get("/", response_model=List[PlanoOut])
def list_planos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    planos = db.query(PlanoPreventiva).filter(PlanoPreventiva.is_active == True).order_by(PlanoPreventiva.proxima_execucao).all()
    return [PlanoOut.model_validate(_enrich(p)) for p in planos]

@router.get("/vencendo")
def vencendo(dias: int = 7, db: Session = Depends(get_db), _=Depends(get_current_user)):
    limite = datetime.now() + timedelta(days=dias)
    planos = db.query(PlanoPreventiva).filter(
        PlanoPreventiva.is_active == True,
        PlanoPreventiva.proxima_execucao <= limite
    ).order_by(PlanoPreventiva.proxima_execucao).all()
    return [PlanoOut.model_validate(_enrich(p)) for p in planos]

@router.post("/", response_model=PlanoOut)
def create_plano(data: PlanoCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    plano = PlanoPreventiva(**data.model_dump())
    db.add(plano)
    db.commit()
    db.refresh(plano)
    return PlanoOut.model_validate(_enrich(plano))

@router.put("/{plano_id}", response_model=PlanoOut)
def update_plano(plano_id: int, data: PlanoUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    plano = db.query(PlanoPreventiva).filter(PlanoPreventiva.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(plano, field, value)
    db.commit()
    db.refresh(plano)
    return PlanoOut.model_validate(_enrich(plano))

@router.post("/{plano_id}/executar")
def executar_plano(plano_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    plano = db.query(PlanoPreventiva).filter(PlanoPreventiva.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    plano.ultima_execucao = datetime.now()
    plano.proxima_execucao = datetime.now() + timedelta(days=plano.frequencia_dias)
    db.commit()
    db.refresh(plano)
    return {"message": "Execução registrada", "proxima": plano.proxima_execucao}

@router.delete("/{plano_id}")
def delete_plano(plano_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    plano = db.query(PlanoPreventiva).filter(PlanoPreventiva.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    plano.is_active = False
    db.commit()
    return {"message": "Plano desativado"}
