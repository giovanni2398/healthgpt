# HealthGPT

Sistema automatizado de agendamento de consultas via WhatsApp com integração ao Google Calendar e fluxo inteligente com ChatGPT.

## Como rodar localmente

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# 🚀 Projeto HealthGPT

Sistema inteligente de atendimento automatizado para clínicas, com agendamento de consultas via WhatsApp, integração com Google Calendar e IA conversacional com ChatGPT.

---

## 📍 Fases do projeto

### 🧱 Fase 1 - Planejamento e arquitetura

- [x] Definir roteiro técnico geral
- [x] Escolher stack (linguagens, frameworks, libs)
- [x] Arquitetura geral do sistema e organização de diretórios
- [x] Planejamento das integrações com APIs (WhatsApp, Google Calendar, OpenAI)
- [x] Ferramentas de versionamento (Git) e ambiente local (VS Code, Python, venv)

---

### ⚙️ Fase 2 - Setup inicial do projeto (etapa atual)

- [x] Criar diretório raiz com Git iniciado
- [x] Instalar dependências (FastAPI, Uvicorn, dotenv etc.)
- [x] Criar `.gitignore`
- [x] Criar `main.py` com servidor básico FastAPI
- [x] Criar pasta `app/` com subpastas e `__init__.py`
- [x] Criar `app/routes/`, `app/services/`, `app/schemas/`
- [ ] Criar `README.md` com descrição e fases do projeto
- [ ] Criar `credentials.json` como placeholder para credenciais (Google API)

---

### 🧠 Fase 3 - Implementação dos serviços e rotas

- [ ] Criar rota do WhatsApp (`/webhook`) que recebe mensagens
- [ ] Integrar com OpenAI para análise da mensagem
- [ ] Verificar convênio aceito ou não
- [ ] Consultar Google Calendar por horários disponíveis
- [ ] Criar evento na agenda com nome e dados do paciente
- [ ] Enviar confirmação do agendamento por WhatsApp

---

### ☁️ Fase 4 - Testes e deploy

- [ ] Testar webhook com Webhook.site ou ngrok
- [ ] Criar testes unitários para serviços (OpenAI, Google Calendar)
- [ ] Preparar `.env.example` para produção
- [ ] Criar Dockerfile (opcional)
- [ ] Deploy na nuvem (Render, Railway, Heroku, GCP etc.)
