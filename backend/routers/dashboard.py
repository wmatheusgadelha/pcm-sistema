from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional
from datetime import datetime, timedelta
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import OrdemServico, Equipamento, PlanoPreventiva, User

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/stats")
def get_stats(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    now = datetime.now()
    ano = ano or now.year
    mes = mes or now.month

    q_base = db.query(OrdemServico)

    total = q_base.count()
    concluidas = q_base.filter(OrdemServico.status == "Concluída").count()
    pendentes = q_base.filter(OrdemServico.status.in_(["Aberta", "Aguardando peça"])).count()
    em_andamento = q_base.filter(OrdemServico.status == "Em andamento").count()

    tempo = db.query(func.sum(OrdemServico.tempo_total)).scalar() or 0

    corretivas = q_base.filter(OrdemServico.tipo == "Corretiva").count()
    preventivas = q_base.filter(OrdemServico.tipo == "Preventiva").count()
    preditivas = q_base.filter(OrdemServico.tipo == "Preditiva").count()
    melhorias = q_base.filter(OrdemServico.tipo == "Melhoria").count()

    total_equip = db.query(Equipamento).filter(Equipamento.is_active == True).count()

    limite_alerta = now + timedelta(days=7)
    prev_vencendo = db.query(PlanoPreventiva).filter(
        PlanoPreventiva.is_active == True,
        PlanoPreventiva.proxima_execucao <= limite_alerta
    ).count()

    linhas_raw = db.query(OrdemServico.linha, func.count(OrdemServico.id)).group_by(OrdemServico.linha).all()
    por_linha = [{"linha": r[0] or "Não informado", "total": r[1]} for r in linhas_raw if r[0]]

    meses_raw = db.query(
        extract('month', OrdemServico.data).label("mes"),
        extract('year', OrdemServico.data).label("ano"),
        func.count(OrdemServico.id).label("total")
    ).filter(extract('year', OrdemServico.data) == ano).group_by("mes", "ano").order_by("mes").all()
    meses_map = {int(r.mes): r.total for r in meses_raw}
    por_mes = [{"mes": m, "total": meses_map.get(m, 0)} for m in range(1, 13)]

    ultimas = q_base.order_by(OrdemServico.created_at.desc()).limit(5).all()
    ultimas_os = [{
        "numero": o.numero,
        "data": o.data.strftime("%d/%m/%Y") if o.data else "",
        "tipo": o.tipo,
        "status": o.status,
        "linha": o.linha,
        "responsavel": o.responsavel_rel.nome if o.responsavel_rel else "—",
        "descricao": (o.descricao[:60] + "...") if o.descricao and len(o.descricao) > 60 else o.descricao
    } for o in ultimas]

    return {
        "total_os": total,
        "os_concluidas": concluidas,
        "os_pendentes": pendentes,
        "os_em_andamento": em_andamento,
        "tempo_total_horas": round(float(tempo), 2),
        "os_corretivas": corretivas,
        "os_preventivas": preventivas,
        "os_preditivas": preditivas,
        "os_melhorias": melhorias,
        "total_equipamentos": total_equip,
        "preventivas_vencendo": prev_vencendo,
        "por_linha": por_linha,
        "por_mes": por_mes,
        "ultimas_os": ultimas_os
    }

@router.get("/relatorio")
def relatorio_completo(
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    q = db.query(OrdemServico)
    if data_inicio: q = q.filter(OrdemServico.data >= data_inicio)
    if data_fim: q = q.filter(OrdemServico.data <= data_fim)

    ordens = q.order_by(OrdemServico.data.desc()).all()
    tempo_total = sum(o.tempo_total or 0 for o in ordens)
    corretivas = [o for o in ordens if o.tipo == "Corretiva"]
    mttr = round(sum(o.tempo_total or 0 for o in corretivas) / len(corretivas), 2) if corretivas else 0

    por_responsavel = {}
    for o in ordens:
        nome = o.responsavel_rel.nome if o.responsavel_rel else "Não atribuído"
        if nome not in por_responsavel:
            por_responsavel[nome] = {"nome": nome, "total_os": 0, "horas": 0}
        por_responsavel[nome]["total_os"] += 1
        por_responsavel[nome]["horas"] += o.tempo_total or 0

    return {
        "periodo": {
            "inicio": data_inicio.isoformat() if data_inicio else None,
            "fim": data_fim.isoformat() if data_fim else None
        },
        "resumo": {
            "total_os": len(ordens),
            "tempo_total_horas": round(tempo_total, 2),
            "mttr_horas": mttr,
            "taxa_conclusao": round(sum(1 for o in ordens if o.status == "Concluída") / len(ordens) * 100, 1) if ordens else 0
        },
        "por_responsavel": list(por_responsavel.values()),
        "ordens": [{
            "numero": o.numero,
            "data": o.data.strftime("%d/%m/%Y") if o.data else "",
            "linha": o.linha,
            "tipo": o.tipo,
            "responsavel": o.responsavel_rel.nome if o.responsavel_rel else "—",
            "tempo": o.tempo_total,
            "status": o.status,
            "materiais": o.materiais
        } for o in ordens]
    }
