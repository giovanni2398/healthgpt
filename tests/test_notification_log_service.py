from datetime import datetime
import unittest

from app.services.notification_log_service import NotificationLogService

class TestNotificationLogService(unittest.TestCase):
    def setUp(self):
        """Configura o ambiente de teste."""
        self.log_service = NotificationLogService()
        self.patient_name = "João Silva"
        self.appointment_date = datetime(2024, 3, 15, 14, 30)
        self.message = "Mensagem de teste"
        self.sent_by = "Sistema"
    
    def test_create_log(self):
        """Testa a criação de um novo log."""
        log = self.log_service.create_log(
            patient_name=self.patient_name,
            appointment_date=self.appointment_date,
            message=self.message,
            sent_by=self.sent_by
        )
        
        # Verifica se o log foi criado corretamente
        self.assertEqual(log.patient_name, self.patient_name)
        self.assertEqual(log.appointment_date, self.appointment_date)
        self.assertEqual(log.message, self.message)
        self.assertEqual(log.sent_by, self.sent_by)
        self.assertEqual(log.status, "pending")
        
        # Verifica se o log foi adicionado à lista
        self.assertIn(log, self.log_service.logs)
    
    def test_get_log(self):
        """Testa a busca de um log pelo ID."""
        # Cria um log
        log = self.log_service.create_log(
            patient_name=self.patient_name,
            appointment_date=self.appointment_date,
            message=self.message,
            sent_by=self.sent_by
        )
        
        # Busca o log pelo ID
        found_log = self.log_service.get_log(log.id)
        
        # Verifica se o log foi encontrado
        self.assertEqual(found_log, log)
        
        # Verifica se retorna None para ID inválido
        self.assertIsNone(self.log_service.get_log("invalid_id"))
    
    def test_get_patient_logs(self):
        """Testa a busca de logs de um paciente."""
        # Cria alguns logs
        log1 = self.log_service.create_log(
            patient_name=self.patient_name,
            appointment_date=self.appointment_date,
            message=self.message,
            sent_by=self.sent_by
        )
        
        log2 = self.log_service.create_log(
            patient_name="Maria Santos",
            appointment_date=self.appointment_date,
            message=self.message,
            sent_by=self.sent_by
        )
        
        # Busca logs do paciente
        patient_logs = self.log_service.get_patient_logs(self.patient_name)
        
        # Verifica se apenas os logs do paciente foram retornados
        self.assertEqual(len(patient_logs), 1)
        self.assertEqual(patient_logs[0], log1)
    
    def test_update_log_status(self):
        """Testa a atualização do status de um log."""
        # Cria um log
        log = self.log_service.create_log(
            patient_name=self.patient_name,
            appointment_date=self.appointment_date,
            message=self.message,
            sent_by=self.sent_by
        )
        
        # Atualiza o status
        success = self.log_service.update_log_status(
            log_id=log.id,
            status="sent",
            notes="Mensagem enviada com sucesso"
        )
        
        # Verifica se a atualização foi bem-sucedida
        self.assertTrue(success)
        self.assertEqual(log.status, "sent")
        self.assertEqual(log.notes, "Mensagem enviada com sucesso")
        
        # Verifica se retorna False para ID inválido
        self.assertFalse(self.log_service.update_log_status("invalid_id", "sent")) 