from typing import Optional, Dict
from app.models.patient import Patient, PatientType, ConversationState
from app.services.patient_state import PatientStateService

class PatientTypeService:
    """Serviço para identificação e gerenciamento do tipo de paciente."""
    
    def __init__(self, patient_state_service: PatientStateService):
        self.patient_state_service = patient_state_service
        self._type_questions = {
            PatientType.UNDEFINED: "Você é paciente particular ou tem convênio?",
            PatientType.PRIVATE: "Ótimo! Você prefere pagar por PIX ou cartão de crédito?",
            PatientType.INSURANCE: "Qual é o seu convênio?"
        }
        
        self._type_keywords = {
            "particular": PatientType.PRIVATE,
            "privado": PatientType.PRIVATE,
            "convênio": PatientType.INSURANCE,
            "plano": PatientType.INSURANCE,
            "unimed": PatientType.INSURANCE,
            "amil": PatientType.INSURANCE,
            "bradesco": PatientType.INSURANCE,
            "sulamerica": PatientType.INSURANCE
        }

    def identify_patient_type(self, message: str, patient: Patient) -> Optional[PatientType]:
        """
        Identifica o tipo de paciente baseado na mensagem recebida.
        Retorna None se não conseguir identificar.
        """
        message_lower = message.lower()
        
        # Procura por palavras-chave na mensagem
        for keyword, patient_type in self._type_keywords.items():
            if keyword in message_lower:
                return patient_type
        
        return None

    def get_next_question(self, patient: Patient) -> str:
        """
        Retorna a próxima pergunta baseada no estado atual do paciente.
        """
        return self._type_questions.get(patient.patient_type, "Desculpe, não entendi. Você é paciente particular ou tem convênio?")

    def update_patient_type(self, patient: Patient, new_type: PatientType) -> Patient:
        """
        Atualiza o tipo do paciente e ajusta o estado da conversa.
        """
        patient.patient_type = new_type
        
        if new_type == PatientType.INSURANCE:
            patient.conversation_state = ConversationState.VALIDATING_INSURANCE
        elif new_type == PatientType.PRIVATE:
            patient.conversation_state = ConversationState.SCHEDULING
        
        return self.patient_state_service.update_patient_info(
            patient_id=patient.id,
            patient_type=new_type
        )

    def handle_patient_response(self, message: str, patient: Patient) -> Dict:
        """
        Processa a resposta do paciente e retorna a próxima ação.
        """
        identified_type = self.identify_patient_type(message, patient)
        
        if identified_type:
            updated_patient = self.update_patient_type(patient, identified_type)
            return {
                "success": True,
                "patient": updated_patient,
                "next_question": self.get_next_question(updated_patient)
            }
        
        return {
            "success": False,
            "patient": patient,
            "next_question": self.get_next_question(patient)
        } 