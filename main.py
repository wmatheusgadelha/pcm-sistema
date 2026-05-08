from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from backend.core.database import Base, engine
from backend.models.user import User, Equipamento, OrdemServico, PlanoPreventiva
from backend.core.security import get_password_hash
from backend.core.database import SessionLocal
from backend.routers import auth, users, equipamentos, ordens, preventivas, dashboard
from backend.services.scheduler import start_scheduler, stop_scheduler

def seed_demo_data():
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return
        admin = User(
            nome="Administrador",
            email="admin@pcm.com",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            cargo="Gestor de Manutenção"
        )
        joao = User(nome="João Silva", email="joao@pcm.com", hashed_password=get_password_hash("senha123"), role="tecnico", cargo="Mecânico Sênior", especialidade="Mecânica")
        carlos = User(nome="Carlos Souza", email="carlos@pcm.com", hashed_password=get_password_hash("senha123"), role="tecnico", cargo="Técnico de Manutenção", especialidade="Eletromecânica")
        ana = User(nome="Ana Lima", email="ana@pcm.com", hashed_password=get_password_hash("senha123"), role="tecnico", cargo="Eletricista Industrial", especialidade="Elétrica")
        db.add_all([admin, joao, carlos, ana])
        db.flush()

        e1 = Equipamento(codigo="EQ-001", nome="Dosador Volumétrico", linha="Linha 1 - Sachê", local="Dosador A", fabricante="Marca X", numero_serie="DS-22-0041", criticidade="Alta")
        e2 = Equipamento(codigo="EQ-002", nome="Seladora Contínua", linha="Linha 3 - Sachê", local="Seladora", fabricante="SealTech", numero_serie="ST-19-8832", criticidade="Alta")
        e3 = Equipamento(codigo="EQ-003", nome="Transportador de Correia", linha="Linha 2 - Sachê", local="Transportador", fabricante="Movitex", numero_serie="MV-20-1155", criticidade="Média")
        e4 = Equipamento(codigo="EQ-004", nome="Máquina Sachê L4", linha="Linha 4 - Sachê", local="Linha 4", criticidade="Alta")
        e5 = Equipamento(codigo="EQ-005", nome="Encartuchadeira", linha="Linha 5 - Cartucho", local="Área 5", fabricante="CartTech", criticidade="Média")
        db.add_all([e1, e2, e3, e4, e5])
        db.flush()

        from datetime import datetime
        os1 = OrdemServico(numero="OS-0001", data=datetime(2025,4,28,7,0), turno="Manhã", hora_inicio="07:00", hora_fim="08:30", tempo_total=1.5, equipamento_id=e1.id, linha="Linha 1 - Sachê", local="Dosador A", tipo="Corretiva", descricao="Troca de mola do dosador volumétrico", materiais="Mola ref. M-12, Parafuso M6", causa="Desgaste por uso", responsavel_id=joao.id, status="Concluída", created_by=admin.id)
        os2 = OrdemServico(numero="OS-0002", data=datetime(2025,4,28,9,0), turno="Manhã", hora_inicio="09:00", hora_fim="10:15", tempo_total=1.25, equipamento_id=e2.id, linha="Linha 3 - Sachê", local="Seladora", tipo="Preventiva", descricao="Lubrificação e regulagem da seladora", materiais="Graxa multiuso 200g", responsavel_id=carlos.id, status="Concluída", observacoes="Próx. preventiva: 30 dias", created_by=admin.id)
        os3 = OrdemServico(numero="OS-0003", data=datetime(2025,4,28,13,0), turno="Tarde", hora_inicio="13:00", hora_fim="14:45", tempo_total=1.75, equipamento_id=e3.id, linha="Linha 2 - Sachê", local="Transportador", tipo="Corretiva", descricao="Substituição de correia transportadora", materiais="Correia B-52, 2 pinos", causa="Correia rompida", responsavel_id=ana.id, status="Concluída", created_by=admin.id)
        db.add_all([os1, os2, os3])

        from datetime import timedelta
        p1 = PlanoPreventiva(equipamento_id=e2.id, tipo="Preventiva", frequencia_dias=30, ultima_execucao=datetime(2025,4,28), proxima_execucao=datetime(2025,5,28), responsavel_id=carlos.id, procedimento="Lubrificação completa e regulagem dos elementos de selagem")
        p2 = PlanoPreventiva(equipamento_id=e1.id, tipo="Preventiva", frequencia_dias=15, proxima_execucao=datetime(2025,5,15), responsavel_id=joao.id, procedimento="Inspeção e ajuste do dosador, limpeza dos bicos")
        p3 = PlanoPreventiva(equipamento_id=e4.id, tipo="Preditiva", frequencia_dias=30, proxima_execucao=datetime(2025,5,20), responsavel_id=ana.id, procedimento="Análise de vibração e termografia")
        db.add_all([p1, p2, p3])
        db.commit()
        print("[SEED] Dados demo criados — admin@pcm.com / admin123")
    except Exception as e:
        db.rollback()
        print(f"[SEED] {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(title="PCM — Sistema de Controle de Manutenção", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(equipamentos.router)
app.include_router(ordens.router)
app.include_router(preventivas.router)
app.include_router(dashboard.router)

if os.path.exists("frontend/static"):
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/", include_in_schema=False)
def serve_frontend():
    index = "frontend/index.html"
    if os.path.exists(index):
        return FileResponse(index)
    return {"message": "PCM API rodando", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}
