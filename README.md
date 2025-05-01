# HealthGPT 📅💬🤖

Sistema simplificado de agendamento inteligente com integração ao Google Calendar, OpenAI e WhatsApp para clínicas de nutrição.

## 🧠 Visão Geral

HealthGPT é um sistema que centraliza o atendimento automatizado via WhatsApp, utiliza IA para análise de mensagens e agenda automaticamente horários disponíveis no Google Calendar. A arquitetura foi simplificada para focar nas funcionalidades essenciais.

## 🎯 Funcionalidades Essenciais

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

## 🚀 Simplificação da Arquitetura

O projeto foi simplificado para manter apenas o essencial:

- **Eliminação da interface web administrativa**
- **Redução de endpoints desnecessários**
- **Remoção do sistema de logs de notificações**
- **Foco nas integrações diretas com APIs externas**

## 🏗 Estrutura do Projeto Simplificada

```bash
HealthGPT/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── whatsapp.py
│   ├── services/
│   │   ├── calendar_service.py
│   │   ├── chatgpt_service.py
│   │   └── whatsapp_service.py
│   └── secrets/
│       └── credentials.json  # <== NÃO versionar este arquivo!
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

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

   Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis essenciais:

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
   PORT=8000
   HOST=0.0.0.0
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

## 🗺️ Roadmap de Desenvolvimento

- **Fase 1: Configuração Base** ✅

  - Estrutura do projeto
  - Configuração de ambiente
  - Integrações básicas

- **Fase 2: Simplificação da Arquitetura** ✅

  - Remoção de funcionalidades não essenciais
  - Foco nas integrações principais
  - Simplificação da estrutura de API

- **Fase 3: Implementação do Fluxo Principal** 🚧

  - Integração WhatsApp → ChatGPT → Google Calendar
  - Processamento de mensagens e confirmações
  - Testes de verificação de disponibilidade

- **Fase 4: Refinamento e Testes**
  - Testes unitários e de integração
  - Ajustes no fluxo de conversação
  - Validação do processo completo

## 🧪 Como Executar

Inicie o servidor FastAPI:

```bash
uvicorn app.main:app --reload
```
