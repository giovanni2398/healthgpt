# HealthGPT Technical Specification

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Core Components](#core-components)
- [Integration Points](#integration-points)
- [Data Flow](#data-flow)
- [State Management](#state-management)
- [Technical Requirements](#technical-requirements)
- [Security Considerations](#security-considerations)
- [Testing Strategy](#testing-strategy)

## Overview

HealthGPT is a WhatsApp-based appointment scheduling system for nutritional consultations. The system leverages natural language processing through ChatGPT to understand patient requests and automates the scheduling process through Google Calendar integration.

**Project Purpose:**
This is a portfolio project developed to demonstrate technical skills in:

- API Integration (WhatsApp, ChatGPT, Google Calendar)
- Python Backend Development
- Natural Language Processing
- System Architecture Design
- Test-Driven Development

**Important Note:**
This project is not intended for production use. It serves as a technical demonstration and learning exercise, showcasing the implementation of various technologies and best practices in software development.

## System Architecture

The system follows a service-oriented architecture with the following key services:

```
[WhatsApp API] <-> [WhatsApp Service] <-> [ChatGPT Service]
                          |
                    [Calendar Service]
                          |
                   [Google Calendar API]
```

## Core Components

### WhatsApp Service (`whatsapp_service.py`)

- Handles incoming WhatsApp messages
- Manages conversation flow and state
- Processes responses and sends messages
- Integrates with other services

Key features:

- Message processing pipeline
- Conversation state management
- Insurance validation
- Document verification
- Appointment confirmation

### ChatGPT Service (`chatgpt_service.py`)

- Natural language processing with humanized, professional secretary-like responses
- Intent recognition for appointment type (private/insurance)
- Insurance provider validation against accepted list
- Date and time extraction and suggestion
- Context management
- Personalized communication style
- Optimal time slot suggestions based on patient preferences

Key features:

- Professional tone maintenance
- Insurance provider verification
- Document requirement communication
- Time slot optimization
- Appointment confirmation messaging

### Calendar Service (`calendar_service.py`)

- Google Calendar integration
- Availability checking
- Appointment creation
- Event management
- Scheduling optimization using patient preferences
- Clinic-specific schedule configuration:
  - Segunda/Quarta/Sexta: 14:00-17:45 (5 slots de 45 minutos)
  - Terça/Quinta/Sábado: 8:30-12:15 (5 slots de 45 minutos)

### ClinicSettings (`clinic_settings.py`)

- Clinic working hours configuration
- Appointment duration and interval settings
- Available slots generation
- Working days management

### Conversation State Manager (`conversation_state.py`)

- State machine implementation
- Conversation flow control
- Data persistence
- Validation logic

## Integration Points

### WhatsApp Cloud API

- **Version**: v19.0
- **Authentication**: Bearer token
- **Endpoints**:
  - Messages: `https://graph.facebook.com/v19.0/{phone-number-id}/messages`
  - Webhook: Receives incoming messages

### OpenAI ChatGPT API

- **Model**: GPT-3.5-turbo
- **System Messages**: Customized for appointment scheduling
- **Response Format**: Structured for intent recognition

### Google Calendar API

- **Scope**: `https://www.googleapis.com/auth/calendar.events`
- **Authentication**: OAuth 2.0
- **Operations**: Read/Write calendar events
- **Current Integration Status**: Mock implementation for testing, pending real API integration for availability checking while maintaining mocks for appointment creation/deletion

## Data Flow

### Appointment Scheduling Flow

#### Private Consultation

```mermaid
sequenceDiagram
    Patient->>WhatsApp: Requests private appointment
    WhatsApp->>ChatGPT: Analyzes request
    ChatGPT->>WhatsApp: Confirms private consultation
    WhatsApp->>Patient: Shows pricing options
    Patient->>WhatsApp: Chooses date/time
    WhatsApp->>Calendar: Checks availability
    Calendar->>WhatsApp: Confirms slot
    WhatsApp->>Patient: Sends confirmation
```

#### Insurance Consultation

```mermaid
sequenceDiagram
    Patient->>WhatsApp: Mentions insurance
    WhatsApp->>ChatGPT: Analyzes insurance info
    ChatGPT->>WhatsApp: Validates insurance
    WhatsApp->>Patient: Requests documents
    Patient->>WhatsApp: Sends documents
    WhatsApp->>Patient: Requests date/time
    Patient->>WhatsApp: Chooses slot
    WhatsApp->>Calendar: Creates appointment
    WhatsApp->>Patient: Sends confirmation
```

## State Management

### Conversation States

- `INITIAL`
- `WAITING_FOR_DATE`
- `WAITING_FOR_TIME`
- `WAITING_FOR_INSURANCE_DOCS`
- `WAITING_FOR_CONFIRMATION`
- `COMPLETED`
- `ERROR`

### State Transitions

```
INITIAL -> WAITING_FOR_DATE (Private)
INITIAL -> WAITING_FOR_INSURANCE_DOCS (Insurance)
WAITING_FOR_INSURANCE_DOCS -> WAITING_FOR_DATE
WAITING_FOR_DATE -> WAITING_FOR_TIME
WAITING_FOR_TIME -> WAITING_FOR_CONFIRMATION
WAITING_FOR_CONFIRMATION -> COMPLETED/ERROR
```

## Technical Requirements

### System Requirements

- Python 3.8+
- FastAPI for API endpoints
- PostgreSQL for data persistence (future implementation)
- Redis for caching (future implementation)

### External Dependencies

- `httpx`: HTTP client
- `python-dotenv`: Environment management
- `pytest`: Testing framework
- `google-auth`: Google authentication
- `openai`: ChatGPT integration

## Security Considerations

### API Security

- All API tokens stored in `.env`
- Webhook verification for WhatsApp
- OAuth 2.0 for Google Calendar
- Rate limiting implementation

### Data Protection

- No PII stored permanently
- Document verification in memory only
- Secure credential management
- HTTPS for all external communications

## Testing Strategy

### Unit Tests

- Service-level testing
- State management validation
- Mock external dependencies

### Integration Tests

- API endpoint testing
- External service integration
- End-to-end flow validation

### Test Coverage

- Minimum 80% coverage required
- Critical paths fully covered
- Error handling scenarios included

## Monitoring and Logging (Future Implementation)

### Metrics to Track

- Message processing time
- External API latency
- Conversation success rate
- Error frequency

### Logging Strategy

- Structured logging
- Error tracking
- Performance monitoring
- User interaction analytics

### Insurance Verification Process

- Validates insurance provider against accepted list
- Requests and verifies insurance card
- Requests and verifies personal ID with photo
- Maintains insurance provider database
- Handles rejection of non-accepted insurance providers

### Calendar Integration Process

- Fetches available slots from Google Calendar
- Suggests optimal times based on:
  - Patient preferences
  - Historical booking patterns
  - Provider availability
- Creates appointments with proper event details
- Sends confirmation with calendar event details
- Handles rescheduling requests

## Implementation Status

The current development status as of February 2024:

### Completed Features

- Clinic schedule configuration
- Appointment optimization algorithm
- Calendar service structure
- Unit tests for scheduling components
- WhatsApp template integration
- ChatGPT message processing
- Basic error handling

### In Progress

- Integration with real Google Calendar API for availability checking
- Secure credential storage implementation

### Pending

- Real-world testing with appointment creation/deletion mocked
- Documentation for new developers

### Portfolio Preparation Plan

1. **Final Integration Testing**

   - Complete end-to-end testing of all features
   - Validation of all API integrations
   - Error handling verification
   - Performance testing

2. **Documentation Updates**

   - Complete API documentation
   - Setup instructions
   - Architecture diagrams
   - Usage examples
   - Screenshots/demonstrations

3. **Code Cleanup**

   - Code style consistency
   - Remove debug logs
   - Optimize imports
   - Update comments

4. **Repository Organization**

   - Clean commit history
   - Version tagging
   - Branch management
   - Issue tracking

5. **Portfolio Presentation**
   - Project overview
   - Technical highlights
   - Architecture decisions
   - Learning outcomes
   - Future improvements

For detailed information about the current implementation status, see [Calendar Integration Status](calendar_integration_status.md).
