# HealthGPT 📅💬🤖

Sistema de agendamento inteligente com integração ao Google Calendar, OpenAI e WhatsApp, voltado para clínicas de nutrição.

## 🧠 Visão Geral

HealthGPT é um sistema modular com backend em Python que centraliza o atendimento automatizado via WhatsApp, utiliza IA para análise de mensagens, agenda automaticamente horários disponíveis no Google Calendar e pode futuramente integrar sistemas de prontuário eletrônico e pagamentos.

## 🎯 Funcionalidades

- **Agendamento Inteligente**

  - Validação automática de horários disponíveis
  - Suporte a agendamentos particulares e por convênio
  - Verificação de convênios aceitos
  - Solicitação e validação de documentos necessários

- **Documentação Necessária**

  - Documento de identificação (obrigatório para todos)
  - Carteirinha do convênio (obrigatório para agendamentos por convênio)

- **Convênios Aceitos**

  - Unimed
  - Amil
  - Bradesco Saúde
  - SulAmérica

- **Integração com WhatsApp**

  - Envio automático de confirmações
  - Solicitação de documentos
  - Notificações de agendamento

- **Integração com Google Calendar**
  - Sincronização automática de agenda
  - Verificação de disponibilidade em tempo real
  - Criação de eventos com detalhes do paciente

---

## 🏗 Estrutura do Projeto

```bash
HealthGPT/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── calendar.py
│   │   └── whatsapp.py
│   ├── models/
│   │   ├── appointment.py
│   │   └── slot.py
│   ├── services/
│   │   ├── appointment_orchestrator.py
│   │   ├── calendar_service.py
│   │   ├── whatsapp_service.py
│   │   ├── notification_service.py
│   │   └── notification_log_service.py
│   ├── utils/
│   │   └── helpers.py
│   ├── tests/
│   │   ├── integration/
│   │   │   └── test_appointment_flow.py
│   │   ├── models/
│   │   │   └── test_appointment.py
│   │   └── services/
│   │       └── test_calendar_service.py
│   └── secrets/
│       └── credentials.json  # <== NÃO versionar este arquivo!
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalação e Setup

1. **Clonar o repositório**

   ```bash
   git clone https://github.com/seu-usuario/HealthGPT.git
   cd HealthGPT
   ```

2. **Criar e ativar o ambiente virtual**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/macOS
   ```

3. **Instalar dependências**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variáveis de ambiente**

   Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

   ```bash
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
   WHATSAPP_API_TOKEN=Bearer xxxxxxxxxxxxxxxxxxx
   GOOGLE_APPLICATION_CREDENTIALS=app/secrets/credentials.json
   GOOGLE_CALENDAR_ID=seu_id_do_calendario@group.calendar.google.com
   ```

---

## 🧱 Fases do Projeto

- **Fase 1 – Integração com Google Calendar** ✅

  - Criar projeto no Google Cloud
  - Ativar API do Google Calendar
  - Conta de serviço e credentials.json
  - Compartilhar calendário com a conta de serviço
  - Criar calendar_service.py com get_available_slots e create_calendar_event

- **Fase 2 – Configuração do .env** ✅

  - Instalar python-dotenv
  - Configurar variáveis sensíveis no .env
  - Usar os.getenv() para carregar paths e tokens

- **Fase 3 – Implementação do Backend (subfases)** ✅

  - 3.1 Estrutura inicial de rotas com FastAPI
  - 3.2 Mock de integração com WhatsApp Business API
  - 3.3 Mock de integração com Google Calendar
  - 3.4 Mock de integração com ChatGPT
  - 3.5 Mock completo do WhatsApp (fluxo de send/receive)
  - 3.6 Orquestração do fluxo de conversa
  - 3.7 Substituir mock do ChatGPT pela chamada real à OpenAI
  - 3.8 Validação de convênios e gerenciamento de estado do paciente

- **Fase 4 – Construção do MVP Funcional** ✅

  - 4.1 Identificação de tipo de paciente (particular vs convênio)
  - 4.2 Verificação de convênios aceitos
  - 4.3 Exibição de horários disponíveis
  - 4.4 Agendamento com confirmação de horário
  - 4.5 Logs e histórico de conversas

- **Fase 5 – Testes, Deploy e Evolução** 🚧
  - 5.1 Testes unitários e integração
  - 5.2 Deploy em nuvem (CI/CD)
  - 5.3 Configurar variáveis de ambiente e segurança
  - 5.4 Testes com usuários reais (beta)

---

## 🧪 Como Rodar os Testes

Execute todos os testes:

```bash
python -m pytest tests/ -v
```

Ou execute testes específicos:

```bash
# Testes de integração
python -m pytest tests/integration/ -v

# Testes de modelos
python -m pytest tests/models/ -v

# Testes de serviços
python -m pytest tests/services/ -v
```

---

## 💻 Terminal Python para Testes Interativos

Abra o terminal Python dentro do ambiente virtual com:

```bash
python
```

E teste, por exemplo:

```python
from app.services.calendar_service import get_available_slots
get_available_slots("2025-04-23")
```

---

## 💡 Dicas para Debug

- Use o Copilot para sugerir correções de sintaxe e testes.
- Utilize `print()` e `logging` para inspecionar variáveis.
- Use VSCode com as extensões Python e DotEnv para facilitar o ambiente.
- Execute os testes com `-v` para ver detalhes de cada teste.
- Use `pytest -k "test_name"` para executar testes específicos.

---

## 🛡 Segurança

Adicione seu `.env` e `credentials.json` no `.gitignore`:

```bash
.env
*.json
```

---

## 🔮 Futuras Etapas

- Integração com WhatsApp API (Twilio ou Z-API)
- Parsing de mensagens com OpenAI
- Interface web para acompanhamento
- Painel de administração
- Integração com sistemas de pagamento e prontuário
- Validação de documentos com OCR
- Integração com sistemas de prontuário eletrônico
- Sistema de lembretes automáticos
- Relatórios e analytics

---

## 🧠 Autor

Gio Nutricionista – Fisiculturista, empreendedor e visionário em saúde, ciência e IA.
