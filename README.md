# HealthGPT 📅💬🤖

Sistema de agendamento inteligente com integração ao Google Calendar, OpenAI e WhatsApp, voltado para clínicas de nutrição.

## 🧠 Visão Geral

HealthGPT é um sistema modular com backend em Python que centraliza o atendimento automatizado via WhatsApp, utiliza IA para análise de mensagens, agenda automaticamente horários disponíveis no Google Calendar e pode futuramente integrar sistemas de prontuário eletrônico e pagamentos.

## 🎯 Funcionalidades

- **Agendamento Inteligente**

  - Oferece opção de autoagendamento via link (Google Appointment Schedules).
  - Permite agendamento conversacional interativo via WhatsApp.
  - Validação automática de horários disponíveis (para fluxo conversacional).
  - Suporte a agendamentos particulares e por convênio
  - Verificação de convênios aceitos

- **Documentação Necessária**

  - Documento de identificação (obrigatório para todos)
  - Carteirinha do convênio (obrigatório para agendamentos por convênio)
  - _Nota:_ No fluxo conversacional, o bot solicitará o envio dos documentos pelo chat. A verificação e armazenamento dos arquivos são realizados manualmente pela equipe.

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

   Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

   ```bash
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-3.5-turbo

   # Google Calendar Configuration
   GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
   GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json

   # WhatsApp Configuration
   WHATSAPP_TOKEN=your_whatsapp_token
   WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
   VERIFY_TOKEN=your_verify_token

   # Application Configuration
   DEBUG=False
   PORT=8000
   HOST=0.0.0.0

   # Database Configuration
   DATABASE_URL=sqlite:///./health_gpt.db

   # Notification Configuration
   NOTIFICATION_ENABLED=True
   NOTIFICATION_INTERVAL=60

   # Clinic Configuration
   CLINIC_NAME=HealthGPT Nutrition Clinic
   CLINIC_ADDRESS=123 Health Street
   CLINIC_PHONE=+1234567890
   CLINIC_EMAIL=contact@healthgpt.com

   # Appointment Configuration
   APPOINTMENT_DURATION=60
   MIN_SCHEDULE_NOTICE=24
   MAX_SCHEDULE_ADVANCE=30
   ```

   ### Descrição das Variáveis de Ambiente

   #### OpenAI Configuration

   - `OPENAI_API_KEY`: Chave de API da OpenAI para integração com ChatGPT
   - `OPENAI_MODEL`: Modelo GPT a ser utilizado (default: gpt-3.5-turbo)

   #### Google Calendar Configuration

   - `GOOGLE_CALENDAR_ID`: ID do calendário do Google para agendamentos
   - `GOOGLE_APPLICATION_CREDENTIALS`: Caminho para o arquivo de credenciais do Google Cloud

   #### WhatsApp Configuration

   - `WHATSAPP_TOKEN`: Token de acesso à API do WhatsApp Business
   - `WHATSAPP_PHONE_NUMBER_ID`: ID do número de telefone no WhatsApp Business
   - `VERIFY_TOKEN`: Token de verificação para webhook do WhatsApp

   #### Application Configuration

   - `DEBUG`: Modo de debug (True/False)
   - `PORT`: Porta da aplicação (default: 8000)
   - `HOST`: Host da aplicação (default: 0.0.0.0)

   #### Database Configuration

   - `DATABASE_URL`: URL de conexão com o banco de dados

   #### Notification Configuration

   - `NOTIFICATION_ENABLED`: Habilita/desabilita notificações
   - `NOTIFICATION_INTERVAL`: Intervalo entre notificações em minutos

   #### Clinic Configuration

   - `CLINIC_NAME`: Nome da clínica
   - `CLINIC_ADDRESS`: Endereço da clínica
   - `CLINIC_PHONE`: Telefone da clínica
   - `CLINIC_EMAIL`: Email da clínica

   #### Appointment Configuration

   - `APPOINTMENT_DURATION`: Duração padrão das consultas em minutos
   - `MIN_SCHEDULE_NOTICE`: Antecedência mínima para agendamento em horas
   - `MAX_SCHEDULE_ADVANCE`: Antecedência máxima para agendamento em dias

---

## 🎯 Fases do Projeto

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

## 🏛️ Arquitetura Atual e Próximos Passos

Atualmente, o backend opera de forma **síncrona**. Isso significa que operações que dependem de respostas externas (como chamadas às APIs do Google, OpenAI ou WhatsApp) bloqueiam a execução até que sejam concluídas. Para um sistema de baixo volume, isso pode ser aceitável.

**Próximos Passos / Melhorias Futuras:**

- **Implementação de Assincronicidade:** Refatorar o código para usar `async` e `await`.
  - **Benefícios:** Maior performance e escalabilidade, especialmente sob carga. O sistema poderá lidar com múltiplas requisições simultâneas de forma mais eficiente, sem que uma requisição lenta bloqueie as outras.
  - **Tecnologias:** Utilizar bibliotecas como `asyncio`, `httpx` (para chamadas HTTP assíncronas) e frameworks compatíveis como FastAPI.
  - **Status:** Planejado para desenvolvimento posterior.

---

## ⏰ Configuração de Horários da Clínica

O sistema permite a configuração personalizada dos horários de atendimento da clínica através do arquivo de configuração JSON localizado em `app/config/clinic_schedule.json`. Esta configuração define os dias e horários de funcionamento e é usada pelo serviço de agendamento para gerar os slots disponíveis.

### Formato do Arquivo de Configuração

```json
{
  "slot_duration_minutes": 45,
  "schedules": [
    {
      "days": [1, 3, 5],
      "description": "Terça, Quinta e Sábado - Manhã",
      "start_time": "08:30",
      "end_time": "12:15"
    },
    {
      "days": [0, 2, 4],
      "description": "Segunda, Quarta e Sexta - Tarde",
      "start_time": "14:00",
      "end_time": "17:45"
    }
  ]
}
```

### Parâmetros de Configuração

- `slot_duration_minutes`: Duração de cada slot de atendimento em minutos
- `schedules`: Lista de configurações de horários
  - `days`: Lista de dias da semana (0 = Segunda, 1 = Terça, ..., 6 = Domingo)
  - `description`: Descrição textual do horário (apenas para referência)
  - `start_time`: Horário de início no formato "HH:MM"
  - `end_time`: Horário de término no formato "HH:MM"

### Personalização para Diferentes Clínicas

Para adaptar o sistema para diferentes clínicas em um ambiente de produção:

1. Edite o arquivo `app/config/clinic_schedule.json` com os horários específicos da clínica
2. Se o arquivo não existir, o sistema criará automaticamente um arquivo com configurações padrão
3. Reinicie a aplicação para que as alterações tenham efeito

### Exemplo para Clínica com Atendimento Noturno

```json
{
  "slot_duration_minutes": 60,
  "schedules": [
    {
      "days": [0, 1, 2, 3, 4],
      "description": "Segunda a Sexta - Manhã e Tarde",
      "start_time": "09:00",
      "end_time": "17:00"
    },
    {
      "days": [1, 3],
      "description": "Terça e Quinta - Noite",
      "start_time": "18:00",
      "end_time": "21:00"
    },
    {
      "days": [5],
      "description": "Sábado - Manhã",
      "start_time": "08:00",
      "end_time": "12:00"
    }
  ]
}
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
