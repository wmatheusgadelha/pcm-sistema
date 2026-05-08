from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..core.security import get_current_user, require_admin
from ..models.user import Equipamento, OrdemServico
from ..schemas.schemas import EquipamentoCreate, EquipamentoUpdate, EquipamentoOut

router = APIRouter(prefix="/api/equipamentos", tags=["equipamentos"])

@router.get("/", response_model=List[EquipamentoOut])
def list_equipamentos(linha: Optional[str] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(Equipamento).filter(Equipamento.is_active == True)
    if linha:
        q = q.filter(Equipamento.linha.ilike(f"%{linha}%"))
    return q.order_by(Equipamento.codigo).all()

@router.post("/", response_model=EquipamentoOut)
def create_equipamento(data: EquipamentoCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if db.query(Equipamento).filter(Equipamento.codigo == data.codigo).first():
        raise HTTPException(status_code=400, detail="Código já cadastrado")
    equip = Equipamento(**data.model_dump())
    db.add(equip)
    db.commit()
    db.refresh(equip)
    return equip

@router.get("/{equip_id}", response_model=EquipamentoOut)
def get_equipamento(equip_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    equip = db.query(Equipamento).filter(Equipamento.id == equip_id).first()
    if not equip:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    return equip

@router.get("/{equip_id}/historico")
def historico_equipamento(equip_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    equip = db.query(Equipamento).filter(Equipamento.id == equip_id).first()
    if not equip:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    ordens = db.query(OrdemServico).filter(OrdemServico.equipamento_id == equip_id).order_by(OrdemServico.data.desc()).all()
    total = len(ordens)
    corretivas = sum(1 for o in ordens if o.tipo == "Corretiva")
    tempo = sum(o.tempo_total or 0 for o in ordens)
    return {
        "equipamento": {"id": equip.id, "codigo": equip.codigo, "nome": equip.nome},
        "total_os": total,
        "corretivas": corretivas,
        "tempo_total_horas": round(tempo, 2),
        "ordens": [{"numero": o.numero, "data": o.data, "tipo": o.tipo, "status": o.status, "descricao": o.descricao} for o in ordens[:20]]
    }

@router.put("/{equip_id}", response_model=EquipamentoOut)
def update_equipamento(equip_id: int, data: EquipamentoUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    equip = db.query(Equipamento).filter(Equipamento.id == equip_id).first()
    if not equip:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(equip, field, value)
    db.commit()
    db.refresh(equip)
    return equip

@router.delete("/{equip_id}")
def delete_equipamento(equip_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    equip = db.query(Equipamento).filter(Equipamento.id == equip_id).first()
    if not equip:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    equip.is_active = False
    db.commit()
    return {"message": "Equipamento desativado"}
