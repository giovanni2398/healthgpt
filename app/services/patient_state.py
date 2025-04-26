from typing import Dict, Optional
from datetime import datetime
from ..models.patient import Patient, PatientType, ConversationState

class PatientStateService:
    """Serviço para gerenciamento de estado dos pacientes."""
    
    def __init__(self):
        # Simula um banco de dados de pacientes
        self._patients: Dict[str, Patient] = {}

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
        insurance_id: Optional[str] = None,
        insurance_card_number: Optional[str] = None
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
        if insurance_card_number:
            patient.insurance_card_number = insurance_card_number

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
        
        if (patient.patient_type == PatientType.INSURANCE and 
            not patient.insurance_id):
            return "Qual é o seu convênio?"
        
        if (patient.patient_type == PatientType.INSURANCE and 
            not patient.insurance_card_number):
            return "Qual é o número da sua carteirinha do convênio?"
        
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