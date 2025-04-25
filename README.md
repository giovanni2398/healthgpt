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

   ```
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
   WHATSAPP_API_TOKEN=Bearer xxxxxxxxxxxxxxxxxxx
   GOOGLE_APPLICATION_CREDENTIALS=app/secrets/credentials.json
   GOOGLE_CALENDAR_ID=seu_id_do_calendario@group.calendar.google.com
   ```

---

## 🧱 Fases do Projeto

- **Fase 1 – Integração com Google Calendar**

  - Criar projeto no Google Cloud
  - Ativar API do Google Calendar
  - Conta de serviço e credentials.json
  - Compartilhar calendário com a conta de serviço
  - Criar calendar_service.py com get_available_slots e create_calendar_event

- **Fase 2 – Configuração do .env**

  - Instalar python-dotenv
  - Configurar variáveis sensíveis no .env
  - Usar os.getenv() para carregar paths e tokens

- **Fase 3 – Implementação do Backend (subfases)**

  - 3.1 Estrutura inicial de rotas com FastAPI
  - 3.2 Mock de integração com WhatsApp Business API
  - 3.3 Mock de integração com Google Calendar
  - 3.4 Mock de integração com ChatGPT
  - 3.5 Mock completo do WhatsApp (fluxo de send/receive)
  - 3.6 Orquestração do fluxo de conversa (em desenvolvimento)
  - 3.7 Substituir mock do ChatGPT pela chamada real à OpenAI
  - 3.8 Validação de convênios e gerenciamento de estado do paciente

- **Fase 4 – Construção do MVP Funcional**

  - 4.1 Identificação de tipo de paciente (particular vs convênio)
  - 4.2 Verificação de convênios aceitos
  - 4.3 Exibição de horários disponíveis
  - 4.4 Agendamento com confirmação de horário
  - 4.5 Logs e histórico de conversas

- **Fase 5 – Testes, Deploy e Evolução**
  - 5.1 Testes unitários e integração
  - 5.2 Deploy em nuvem (CI/CD)
  - 5.3 Configurar variáveis de ambiente e segurança
  - 5.4 Testes com usuários reais (beta)

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

---

## 🛡 Segurança

Adicione seu `.env` e `credentials.json` no `.gitignore`:

```
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

---

## 🧠 Autor

Gio Nutricionista – Fisiculturista, empreendedor e visionário em saúde, ciência e IA.
