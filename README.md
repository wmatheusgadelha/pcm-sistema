# ⚙ PCM — Sistema de Planejamento e Controle de Manutenção

Sistema completo de PCM com FastAPI (Python), PostgreSQL, JWT Auth e alertas por e-mail.

---

## 🚀 Rodando localmente

### 1. Pré-requisitos
- Python 3.11+
- pip

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

Para rodar **localmente sem PostgreSQL**, o sistema usa SQLite automaticamente — não precisa configurar nada.

### 4. Iniciar o servidor
```bash
uvicorn main:app --reload
```

Acesse: **http://localhost:8000**

Login padrão criado automaticamente:
- **E-mail:** admin@pcm.com
- **Senha:** admin123

### 5. Documentação da API
Acesse: **http://localhost:8000/docs**

---

## ☁️ Deploy no Render (gratuito)

### Passo 1 — GitHub
1. Crie um repositório no GitHub
2. Suba todos os arquivos deste projeto

### Passo 2 — Render
1. Acesse [render.com](https://render.com) e crie uma conta
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub
4. Configure:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Passo 3 — Banco de dados
1. No Render, clique em **"New +"** → **"PostgreSQL"**
2. Crie um banco gratuito chamado `pcm-db`
3. Copie a **Connection String**
4. Cole em **Environment Variables** → `DATABASE_URL`

### Passo 4 — Variáveis de ambiente no Render
```
SECRET_KEY          = (gere uma string aleatória longa)
DATABASE_URL        = (connection string do PostgreSQL)
MAIL_USERNAME       = seu-email@gmail.com
MAIL_PASSWORD       = sua-senha-de-app-gmail
MAIL_FROM           = seu-email@gmail.com
```

### Passo 5 — E-mail Gmail
1. Acesse sua conta Google → Segurança → Verificação em 2 etapas (ativar)
2. Volte em Segurança → **Senhas de app**
3. Gere uma senha para "Outro (PCM)"
4. Use essa senha em `MAIL_PASSWORD`

---

## 📋 Funcionalidades

- ✅ **Dashboard** — KPIs, gráficos por tipo e linha, últimas OS, preventivas vencendo
- ✅ **Ordens de Serviço** — CRUD completo, filtros, busca
- ✅ **Programação** — Plano de preventivas com frequência configurável
- ✅ **Equipamentos** — Cadastro com código, criticidade, histórico
- ✅ **Colaboradores** — Gestão de equipe com perfis e especialidades
- ✅ **Relatórios** — MTTR, taxa de conclusão, histórico completo
- ✅ **Autenticação** — JWT com 3 níveis: Admin, Gestor, Técnico
- ✅ **E-mails automáticos** — Alertas de preventivas vencendo (diário 07:00), nova OS criada, boas-vindas

## 🔑 Perfis de acesso

| Perfil   | Permissões                                    |
|----------|-----------------------------------------------|
| Admin    | Tudo, incluindo gerenciar usuários            |
| Gestor   | Tudo exceto excluir usuários                  |
| Técnico  | Ver, criar e editar OS/preventivas            |

## 📡 API REST — Endpoints principais

```
POST   /api/auth/token              Login
GET    /api/dashboard/stats         Indicadores do dashboard
GET    /api/dashboard/relatorio     Relatório completo
GET    /api/os/                     Listar OS (filtros: tipo, status, search)
POST   /api/os/                     Criar OS
PUT    /api/os/{id}                 Atualizar OS
GET    /api/equipamentos/           Listar equipamentos
POST   /api/equipamentos/           Cadastrar equipamento
GET    /api/preventivas/            Listar planos
POST   /api/preventivas/            Criar plano
POST   /api/preventivas/{id}/executar  Registrar execução
GET    /api/users/                  Listar colaboradores
POST   /api/users/                  Cadastrar colaborador
```

Documentação interativa completa em `/docs` (Swagger UI).

---

## 🗂️ Estrutura do projeto

```
pcm-system/
├── main.py                    # Entrada da aplicação
├── requirements.txt
├── render.yaml                # Deploy automático no Render
├── .env.example
├── backend/
│   ├── core/
│   │   ├── config.py          # Configurações / variáveis de ambiente
│   │   ├── database.py        # Conexão SQLAlchemy
│   │   └── security.py        # JWT, hashing, permissões
│   ├── models/
│   │   └── user.py            # Todos os modelos SQLAlchemy
│   ├── schemas/
│   │   └── schemas.py         # Schemas Pydantic
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── equipamentos.py
│   │   ├── ordens.py
│   │   ├── preventivas.py
│   │   └── dashboard.py
│   └── services/
│       ├── email_service.py   # Envio de e-mails
│       └── scheduler.py       # Alertas automáticos
└── frontend/
    └── index.html             # Frontend completo (SPA)
```
