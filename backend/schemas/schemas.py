from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime

# ── Auth ──────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class LoginRequest(BaseModel):
    email: str
    password: str

# ── User ──────────────────────────────────────────────
class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    password: str
    role: str = "tecnico"
    especialidade: Optional[str] = None
    cargo: Optional[str] = None
    telefone: Optional[str] = None
    matricula: Optional[str] = None

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    role: Optional[str] = None
    especialidade: Optional[str] = None
    cargo: Optional[str] = None
    telefone: Optional[str] = None
    is_active: Optional[bool] = None

class UserOut(BaseModel):
    id: int
    nome: str
    email: str
    role: str
    especialidade: Optional[str]
    cargo: Optional[str]
    telefone: Optional[str]
    matricula: Optional[str]
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

# ── Equipamento ───────────────────────────────────────
class EquipamentoCreate(BaseModel):
    codigo: str
    nome: str
    linha: str
    local: Optional[str] = None
    fabricante: Optional[str] = None
    modelo: Optional[str] = None
    numero_serie: Optional[str] = None
    data_instalacao: Optional[datetime] = None
    criticidade: str = "Média"
    observacoes: Optional[str] = None

class EquipamentoUpdate(BaseModel):
    nome: Optional[str] = None
    linha: Optional[str] = None
    local: Optional[str] = None
    fabricante: Optional[str] = None
    modelo: Optional[str] = None
    numero_serie: Optional[str] = None
    criticidade: Optional[str] = None
    observacoes: Optional[str] = None
    is_active: Optional[bool] = None

class EquipamentoOut(BaseModel):
    id: int
    codigo: str
    nome: str
    linha: str
    local: Optional[str]
    fabricante: Optional[str]
    modelo: Optional[str]
    numero_serie: Optional[str]
    data_instalacao: Optional[datetime]
    criticidade: str
    observacoes: Optional[str]
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

# ── Ordem de Serviço ──────────────────────────────────
class OSCreate(BaseModel):
    data: datetime
    turno: Optional[str] = None
    hora_inicio: Optional[str] = None
    hora_fim: Optional[str] = None
    tempo_total: Optional[float] = None
    equipamento_id: Optional[int] = None
    linha: Optional[str] = None
    local: Optional[str] = None
    tipo: str
    descricao: str
    materiais: Optional[str] = None
    causa: Optional[str] = None
    responsavel_id: Optional[int] = None
    status: str = "Aberta"
    observacoes: Optional[str] = None

class OSUpdate(BaseModel):
    data: Optional[datetime] = None
    turno: Optional[str] = None
    hora_inicio: Optional[str] = None
    hora_fim: Optional[str] = None
    tempo_total: Optional[float] = None
    linha: Optional[str] = None
    local: Optional[str] = None
    tipo: Optional[str] = None
    descricao: Optional[str] = None
    materiais: Optional[str] = None
    causa: Optional[str] = None
    responsavel_id: Optional[int] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

class OSOut(BaseModel):
    id: int
    numero: str
    data: datetime
    turno: Optional[str]
    hora_inicio: Optional[str]
    hora_fim: Optional[str]
    tempo_total: Optional[float]
    equipamento_id: Optional[int]
    linha: Optional[str]
    local: Optional[str]
    tipo: str
    descricao: str
    materiais: Optional[str]
    causa: Optional[str]
    responsavel_id: Optional[int]
    status: str
    observacoes: Optional[str]
    created_at: datetime
    equipamento_nome: Optional[str] = None
    responsavel_nome: Optional[str] = None
    class Config:
        from_attributes = True

# ── Plano Preventiva ─────────────────────────────────
class PlanoCreate(BaseModel):
    equipamento_id: int
    tipo: str
    frequencia_dias: int
    proxima_execucao: datetime
    responsavel_id: Optional[int] = None
    procedimento: Optional[str] = None

class PlanoUpdate(BaseModel):
    tipo: Optional[str] = None
    frequencia_dias: Optional[int] = None
    proxima_execucao: Optional[datetime] = None
    responsavel_id: Optional[int] = None
    procedimento: Optional[str] = None
    is_active: Optional[bool] = None

class PlanoOut(BaseModel):
    id: int
    equipamento_id: int
    tipo: str
    frequencia_dias: int
    ultima_execucao: Optional[datetime]
    proxima_execucao: datetime
    responsavel_id: Optional[int]
    procedimento: Optional[str]
    is_active: bool
    equipamento_nome: Optional[str] = None
    responsavel_nome: Optional[str] = None
    class Config:
        from_attributes = True

# ── Dashboard ─────────────────────────────────────────
class DashboardStats(BaseModel):
    total_os: int
    os_concluidas: int
    os_pendentes: int
    os_em_andamento: int
    tempo_total_horas: float
    os_corretivas: int
    os_preventivas: int
    os_preditivas: int
    os_melhorias: int
    total_equipamentos: int
    preventivas_vencendo: int
    por_linha: List[dict]
    por_mes: List[dict]
    ultimas_os: List[dict]
