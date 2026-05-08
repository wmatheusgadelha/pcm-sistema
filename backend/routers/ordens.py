from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import datetime
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import OrdemServico, Equipamento, User
from ..schemas.schemas import OSCreate, OSUpdate, OSOut
from ..services.email_service import send_os_created

router = APIRouter(prefix="/api/os", tags=["ordens-servico"])

def _next_numero(db: Session) -> str:
    last = db.query(OrdemServico).order_by(OrdemServico.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"OS-{num:04d}"

def _enrich(os: OrdemServico) -> dict:
    d = {c.name: getattr(os, c.name) for c in os.__table__.columns}
    d["equipamento_nome"] = os.equipamento_rel.nome if os.equipamento_rel else None
    d["responsavel_nome"] = os.responsavel_rel.nome if os.responsavel_rel else None
    return d

@router.get("/", response_model=List[OSOut])
def list_os(
    tipo: Optional[str] = None,
    status: Optional[str] = None,
    responsavel_id: Optional[int] = None,
    equipamento_id: Optional[int] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    q = db.query(OrdemServico)
    if tipo: q = q.filter(OrdemServico.tipo == tipo)
    if status: q = q.filter(OrdemServico.status == status)
    if responsavel_id: q = q.filter(OrdemServico.responsavel_id == responsavel_id)
    if equipamento_id: q = q.filter(OrdemServico.equipamento_id == equipamento_id)
    if data_inicio: q = q.filter(OrdemServico.data >= data_inicio)
    if data_fim: q = q.filter(OrdemServico.data <= data_fim)
    if search: q = q.filter(OrdemServico.descricao.ilike(f"%{search}%") | OrdemServico.linha.ilike(f"%{search}%"))
    ordens = q.order_by(OrdemServico.data.desc()).offset(offset).limit(limit).all()
    result = []
    for os in ordens:
        d = OSOut.model_validate(_enrich(os))
        result.append(d)
    return result

@router.post("/", response_model=OSOut)
def create_os(data: OSCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    os = OrdemServico(
        numero=_next_numero(db),
        created_by=current_user.id,
        **data.model_dump()
    )
    db.add(os)
    db.commit()
    db.refresh(os)
    if os.responsavel_rel:
        emails = [os.responsavel_rel.email]
        admins = db.query(User).filter(User.role.in_(["admin", "gestor"]), User.is_active == True).all()
        for a in admins:
            if a.email not in emails:
                emails.append(a.email)
        equip_nome = os.equipamento_rel.nome if os.equipamento_rel else (os.linha or "Equipamento")
        send_os_created(emails, os.numero, equip_nome, os.tipo, os.responsavel_rel.nome, os.descricao[:100])
    return OSOut.model_validate(_enrich(os))

@router.get("/{os_id}", response_model=OSOut)
def get_os(os_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os:
        raise HTTPException(status_code=404, detail="OS não encontrada")
    return OSOut.model_validate(_enrich(os))

@router.put("/{os_id}", response_model=OSOut)
def update_os(os_id: int, data: OSUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os:
        raise HTTPException(status_code=404, detail="OS não encontrada")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(os, field, value)
    db.commit()
    db.refresh(os)
    return OSOut.model_validate(_enrich(os))

@router.delete("/{os_id}")
def delete_os(os_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os:
        raise HTTPException(status_code=404, detail="OS não encontrada")
    db.delete(os)
    db.commit()
    return {"message": "OS removida"}
