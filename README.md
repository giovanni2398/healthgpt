# HealthGPT 🏥

Um sistema inteligente de agendamento de consultas nutricionais via WhatsApp, utilizando ChatGPT para processamento de linguagem natural.

## 🧠 Visão Geral

HealthGPT é um sistema que centraliza o atendimento automatizado via WhatsApp, utiliza IA para análise de mensagens e agenda automaticamente horários disponíveis no Google Calendar. A arquitetura foi simplificada para focar nas funcionalidades essenciais.

**Propósito:** Este projeto foi desenvolvido exclusivamente como um exercício de aprendizado e para compor um portfólio técnico, demonstrando a integração de tecnologias como IA (ChatGPT), APIs externas (WhatsApp Cloud API, Google Calendar API) e desenvolvimento de serviços backend em Python.

**Importante:** Este projeto não foi desenvolvido para uso em produção. É um projeto demonstrativo que visa:

- Demonstrar habilidades técnicas em integração de APIs
- Mostrar conhecimentos em desenvolvimento Python
- Servir como exemplo de implementação de sistemas com IA
- Compor um portfólio técnico

## 🌟 Funcionalidades

- **Agendamento Inteligente**: Processamento de linguagem natural para entender as solicitações dos pacientes
- **Integração WhatsApp**: Comunicação direta via WhatsApp usando a API oficial do WhatsApp Cloud
- **Gestão de Convênios**: Suporte a diversos convênios médicos e consultas particulares
- **Integração Calendário**: Sincronização automática com Google Calendar
- **Validação de Documentos**: Verificação de documentos e carteirinha de convênio
- **Confirmação Automática**: Envio automático de confirmações de agendamento

### Funcionalidades Essenciais

- **Conversa Automatizada (ChatGPT)**

  - Recebimento e análise de mensagens do paciente
  - Identificação de intenções (agendamento, informações)
  - Processamento de linguagem natural para extração de datas/horários

- **Gestão de Agenda (Google Calendar)**

  - Verificação de disponibilidade de horários
  - Criação de eventos de consulta
  - Confirmação de agendamento

- **Comunicação com Pacientes (WhatsApp)**
  - Recebimento de mensagens via webhook
  - Envio de confirmações de agendamento
  - Respostas automatizadas

## 🚀 Começando

### Pré-requisitos

- Python 3.8+
- Conta de desenvolvedor do WhatsApp Business API
- Projeto configurado no Google Cloud com acesso à API do Calendar
- Arquivo `.env` com as credenciais necessárias

### Instalação

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/HealthGPT.git
cd HealthGPT
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente no arquivo `.env`:

```env
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
PORT=8000
HOST=0.0.0.0
```

## 📱 Fluxo de Agendamento

O sistema suporta dois tipos de agendamento:

### Consulta Particular

1. Paciente solicita agendamento particular
2. Sistema informa valores e opções disponíveis
3. Paciente escolhe data e horário
4. Sistema confirma agendamento e envia detalhes

### Consulta por Convênio

1. Paciente informa convênio
2. Sistema verifica se o convênio é aceito
3. Paciente envia documentação (carteirinha e documento com foto)
4. Paciente escolhe data e horário
5. Sistema confirma agendamento e envia detalhes

## 🔧 Desenvolvimento

### Estrutura do Projeto

```
HealthGPT/
├── app/
│   ├── config/
│   │   ├── clinic_settings.py
│   │   └── config.py
│   ├── services/
│   │   ├── whatsapp_service.py
│   │   ├── chatgpt_service.py
│   │   ├── calendar_service.py
│   │   ├── scheduling_preferences.py
│   │   ├── insurance_service.py
│   │   └── conversation_state.py
│   ├── tests/
│   │   ├── test_calendar_service.py
│   │   ├── test_chatgpt.py
│   │   ├── test_clinic_settings.py
│   │   ├── test_scheduling_optimizer.py
│   │   ├── test_insurance_service.py
│   │   ├── test_whatsapp_service.py
│   │   └── test_conversation_state.py
│   └── secrets/
│       ├── credentials.json
│       └── token.json
├── tests/
│   └── services/
│       └── test_simplified_slot_service.py
├── docs/
│   ├── tech_specs.md
│   └── calendar_integration_status.md
├── .env
├── requirements.txt
└── README.md
```

### Executando Testes

```bash
pytest app/tests/ -v
```

## 📊 Fluxo de Funcionamento

1. **Recebimento da Mensagem**

   - Paciente envia mensagem via WhatsApp
   - Webhook recebe e processa a mensagem

2. **Análise da Mensagem**

   - ChatGPT analisa a mensagem do paciente
   - Identifica intenção de agendamento e detalhes (data/hora)

3. **Verificação de Disponibilidade**

   - Sistema consulta o Google Calendar
   - Verifica slots disponíveis para a data solicitada

4. **Confirmação e Agendamento**
   - Consulta é registrada no Google Calendar
   - Confirmação é enviada ao paciente via WhatsApp

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **APIs:** OpenAI API (ChatGPT), WhatsApp Cloud API (Meta), Google Calendar API
- **Bibliotecas Principais:** `httpx`, `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`, `openai`, `python-dotenv`, `pytest`
- **Gerenciamento de Estado:** Dicionário em memória (`app/services/conversation_state.py`)
- **Framework Web:** [Ainda não definido/utilizado diretamente - ex: Flask/FastAPI pode ser adicionado se relevante]

## 🗺️ Roadmap de Desenvolvimento

- **Fase 1: Configuração Base** ✅

  - Estrutura do projeto
  - Configuração de ambiente
  - Integrações básicas

- **Fase 2: Simplificação da Arquitetura** ✅

  - Remoção de funcionalidades não essenciais
  - Foco nas integrações principais
  - Simplificação da estrutura de API

- **Fase 3: Implementação do Fluxo Principal** ✅

  - Integração WhatsApp → ChatGPT → Google Calendar
  - Processamento de mensagens e confirmações
  - Testes de verificação de disponibilidade
  - **Status Atual:** A integração entre WhatsApp, ChatGPT e Google Calendar está completamente funcional. O sistema agora suporta:
    - Envio de templates de confirmação via WhatsApp
    - Versionamento de templates (v1, v2, etc.)
    - Parâmetros nomeados para personalização
    - Confirmação automática de agendamentos
    - Logs detalhados para monitoramento

### Templates do WhatsApp

O sistema utiliza templates aprovados pela Meta para envio de mensagens. Atualmente implementados:

1. **appointment_confirmation_v2**
   - Parâmetros:
     - `paciente`: Nome do paciente
     - `data`: Data e hora da consulta (formato: DD/MM/YYYY - HH:MM)
   - Versão atual: v2
   - Status: ✅ Funcional

### Boas Práticas Implementadas

- Versionamento de templates
- Parâmetros nomeados
- Logs detalhados
- Tratamento de erros
- Validação de parâmetros

## 📚 Documentação

Para informações mais detalhadas sobre a implementação, fluxos e funcionalidades, consulte:

- [Documentação Técnica](docs/tech_specs.md) - Visão geral técnica do sistema
- [Status da Integração com Google Calendar](docs/calendar_integration_status.md) - Status atual e próximos passos da integração com o Google Calendar

## 🤝 Contribuindo

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ✨ Agradecimentos

- OpenAI pela API do ChatGPT
- Meta pela API do WhatsApp
- Google pela API do Calendar
