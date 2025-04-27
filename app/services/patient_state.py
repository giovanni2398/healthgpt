from typing import Dict, Optional
from datetime import datetime
from ..models.patient import Patient, PatientType, ConversationState, InsuranceStatus
from ..services.insurance_service import InsuranceService

class PatientStateService:
    """Serviço para gerenciamento de estado dos pacientes."""
    
    def __init__(self):
        # Simula um banco de dados de pacientes
        self._patients: Dict[str, Patient] = {}
        self.insurance_service = InsuranceService()

    def get_or_create_patient(self, phone: str) -> Patient:
        """
        Retorna um paciente existente ou cria um novo baseado no telefone.
        O telefone é usado como ID pois é o identificador no WhatsApp.
        """
        if phone not in self._patients:
            self._patients[phone] = Patient(
                id=phone,
                phone=phone,
                conversation_state=ConversationState.INITIAL
            )
        return self._patients[phone]

    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Retorna um paciente pelo ID."""
        return self._patients.get(patient_id)

    def update_patient_info(
        self,
        patient_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        patient_type: Optional[PatientType] = None,
        insurance_id: Optional[str] = None
    ) -> Patient:
        """Atualiza informações do paciente."""
        patient = self.get_patient(patient_id)
        if not patient:
            raise ValueError(f"Paciente {patient_id} não encontrado")

        if name:
            patient.name = name
        if email:
            patient.email = email
        if patient_type:
            patient.patient_type = patient_type
        if insurance_id:
            patient.insurance_id = insurance_id
            # Atualiza o status do convênio
            accepted_plans = [plan.id for plan in self.insurance_service.get_accepted_plans()]
            if insurance_id in accepted_plans:
                patient.insurance_status = InsuranceStatus.WAITING_DOCS
                # Registra o convênio no serviço de convênios
                self.insurance_service.register_insurance(patient_id, insurance_id)
            else:
                patient.insurance_status = InsuranceStatus.INVALID

        return patient

    def update_conversation_state(
        self,
        patient_id: str,
        new_state: ConversationState
    ) -> Patient:
        """Atualiza o estado da conversa do paciente."""
        patient = self.get_patient(patient_id)
        if not patient:
            raise ValueError(f"Paciente {patient_id} não encontrado")

        patient.update_state(new_state)
        return patient

    def mark_insurance_documents_received(
        self,
        patient_id: str,
        insurance_id: str
    ) -> Patient:
        """Marca que os documentos do convênio foram recebidos."""
        patient = self.get_patient(patient_id)
        if not patient:
            raise ValueError(f"Paciente {patient_id} não encontrado")

        if patient.insurance_id != insurance_id:
            raise ValueError("Convênio não corresponde ao registrado")

        # Marca documentos como recebidos no serviço de convênios
        self.insurance_service.mark_documents_received(patient_id, insurance_id)
        
        # Atualiza status do paciente
        patient.insurance_status = InsuranceStatus.VALIDATED
        
        # Atualiza estado da conversa para agendamento
        patient.conversation_state = ConversationState.SCHEDULING
        
        return patient

    def get_next_question(self, patient: Patient) -> str:
        """
        Retorna a próxima pergunta baseada no estado atual do paciente.
        Usado para guiar o fluxo da conversa.
        """
        if not patient.name:
            return "Qual é o seu nome completo?"
        
        if patient.patient_type == PatientType.UNDEFINED:
            return ("Como você prefere realizar o atendimento?\n"
                   "1 - Particular\n"
                   "2 - Convênio")
        
        if patient.patient_type == PatientType.INSURANCE:
            if not patient.insurance_id:
                return "Qual é o seu convênio?"
            elif patient.insurance_status == InsuranceStatus.WAITING_DOCS:
                return ("Por favor, envie uma foto do seu documento de identificação "
                       "e da sua carteirinha do convênio.")
            elif patient.insurance_status == InsuranceStatus.INVALID:
                return "Desculpe, não atendemos este convênio. Gostaria de agendar como particular?"
        
        if not patient.email:
            return "Qual é o seu e-mail para envio da confirmação?"
        
        return "Agora podemos verificar os horários disponíveis para agendamento."

    def reset_conversation(self, patient_id: str) -> None:
        """
        Reseta o estado da conversa do paciente mantendo suas informações básicas.
        Útil quando uma conversa é interrompida ou finalizada.
        """
        patient = self.get_patient(patient_id)
        if patient:
            patient.conversation_state = ConversationState.INITIAL
            patient.clear_context()
            patient.last_interaction = datetime.now() 