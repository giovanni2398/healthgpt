# HealthGPT 📅💬🤖

Sistema de agendamento inteligente com integração ao Google Calendar, OpenAI e WhatsApp, voltado para clínicas de nutrição.

## 🧠 Visão Geral

HealthGPT é um sistema modular com backend em Python que centraliza o atendimento automatizado via WhatsApp, utiliza IA para análise de mensagens, agenda automaticamente horários disponíveis no Google Calendar e pode futuramente integrar sistemas de prontuário eletrônico e pagamentos.

---

## 🏗 Estrutura do Projeto

```bash
HealthGPT/
├── app/
│   ├── main.py
│   ├── services/
│   │   ├── calendar_service.py
│   │   └── whatsapp_service.py
│   ├── utils/
│   │   └── helpers.py
│   ├── tests/
│   │   └── test_calendar.py
│   └── secrets/
│       └── credentials.json  # <== NÃO versionar este arquivo!
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalação e Setup

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/HealthGPT.git
cd HealthGPT
```

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 🔐 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
WHATSAPP_API_TOKEN=Bearer xxxxxxxxxxxxxxxxxxx
GOOGLE_APPLICATION_CREDENTIALS=app/secrets/credentials.json
GOOGLE_CALENDAR_ID=seu_id_do_calendario@group.calendar.google.com
```

---

## 🔧 Roteiro Completo de Implementação

### ✅ Etapa 1: Integração com Google Calendar

- [x] Criar projeto no Google Cloud
- [x] Ativar API do Google Calendar
- [x] Criar conta de serviço e gerar `credentials.json`
- [x] Compartilhar o calendário com a conta de serviço
- [x] Criar `calendar_service.py` com:
  - Autenticação com `google.oauth2`
  - Função `get_available_slots`
  - Função `create_calendar_event`

### ✅ Etapa 2: Configuração do `.env`

- [x] Instalar `python-dotenv`
- [x] Configurar variáveis sensíveis no `.env`
- [x] Usar `os.getenv()` para carregar paths e tokens

### ✅ Etapa 3: Testes Locais com Python CLI

- [x] Criar `test_calendar.py`
- [x] Rodar com:

  ```bash
  python -m app.tests.test_calendar
  ```

### ✅ Etapa 4: Corrigir Paths e Imports

- [x] Usar imports absolutos baseados no módulo `app`
- [x] Corrigir erros de `ImportError` e `FileNotFoundError`

---

## 🧪 Como Rodar os Testes

Execute:

```bash
python -m app.tests.test_calendar
```

Esse teste faz:

- Autenticação via Google
- Listagem dos horários livres no dia informado

---

## 💻 Terminal Python para Testes Interativos

Você pode abrir o terminal Python dentro do ambiente virtual com:

```bash
python
```

E testar, por exemplo:

```python
from app.services.calendar_service import get_available_slots
get_available_slots("2025-04-23")
```

---

## 💡 Dicas para Debug

- Use o Copilot para sugerir correções de sintaxe e testes.
- Utilize `print()` e `logging` para inspecionar variáveis.
- Use VSCode com `Python` e `DotEnv` extensions para facilitar o ambiente.

---

## 🛡 Segurança

Adicione seu `.env` e `credentials.json` no `.gitignore`:

```gitignore
.env
*.json
```

---

## 🔮 Futuras Etapas

- [ ] Integração com WhatsApp API (Twilio ou Z-API)
- [ ] Parsing de mensagens com OpenAI
- [ ] Interface web para acompanhamento
- [ ] Painel de administração
- [ ] Integração com sistemas de pagamento e prontuário

---

## 🧠 Autor

Gio Nutricionista – Fisiculturista, empreendedor e visionário em saúde, ciência e IA.
