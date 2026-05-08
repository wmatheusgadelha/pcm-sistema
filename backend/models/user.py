from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base

class UserRole(str, enum.Enum):
    admin = "admin"
    gestor = "gestor"
    tecnico = "tecnico"

class OSType(str, enum.Enum):
    corretiva = "Corretiva"
    preventiva = "Preventiva"
    preditiva = "Preditiva"
    melhoria = "Melhoria"

class OSStatus(str, enum.Enum):
    aberta = "Aberta"
    em_andamento = "Em andamento"
    aguardando_peca = "Aguardando peça"
    concluida = "Concluída"
    cancelada = "Cancelada"

class Criticidade(str, enum.Enum):
    alta = "Alta"
    media = "Média"
    baixa = "Baixa"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="tecnico")
    especialidade = Column(String(100))
    cargo = Column(String(100))
    telefone = Column(String(20))
    matricula = Column(String(30), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ordens = relationship("OrdemServico", back_populates="responsavel_rel")

class Equipamento(Base):
    __tablename__ = "equipamentos"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(30), unique=True, index=True, nullable=False)
    nome = Column(String(150), nullable=False)
    linha = Column(String(100), nullable=False)
    local = Column(String(100))
    fabricante = Column(String(100))
    modelo = Column(String(100))
    numero_serie = Column(String(100))
    data_instalacao = Column(DateTime)
    criticidade = Column(String(20), default="Média")
    observacoes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ordens = relationship("OrdemServico", back_populates="equipamento_rel")
    preventivas = relationship("PlanoPreventiva", back_populates="equipamento_rel")

class OrdemServico(Base):
    __tablename__ = "ordens_servico"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), unique=True, index=True, nullable=False)
    data = Column(DateTime, nullable=False)
    turno = Column(String(20))
    hora_inicio = Column(String(10))
    hora_fim = Column(String(10))
    tempo_total = Column(Float)
    equipamento_id = Column(Integer, ForeignKey("equipamentos.id"))
    linha = Column(String(100))
    local = Column(String(100))
    tipo = Column(String(20), nullable=False)
    descricao = Column(Text, nullable=False)
    materiais = Column(Text)
    causa = Column(Text)
    responsavel_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(30), default="Aberta")
    observacoes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    equipamento_rel = relationship("Equipamento", back_populates="ordens")
    responsavel_rel = relationship("User", foreign_keys=[responsavel_id], back_populates="ordens")

class PlanoPreventiva(Base):
    __tablename__ = "planos_preventiva"
    id = Column(Integer, primary_key=True, index=True)
    equipamento_id = Column(Integer, ForeignKey("equipamentos.id"), nullable=False)
    tipo = Column(String(50), nullable=False)
    frequencia_dias = Column(Integer, nullable=False)
    ultima_execucao = Column(DateTime)
    proxima_execucao = Column(DateTime, nullable=False)
    responsavel_id = Column(Integer, ForeignKey("users.id"))
    procedimento = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    equipamento_rel = relationship("Equipamento", back_populates="preventivas")
    responsavel_rel = relationship("User", foreign_keys=[responsavel_id])
