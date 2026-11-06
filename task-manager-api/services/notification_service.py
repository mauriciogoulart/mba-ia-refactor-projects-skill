import logging
import smtplib

from config.logging_config import mask_email
from utils.helpers import utc_now

logger = logging.getLogger(__name__)


class NotificationService:
    """Envio de e-mails de notificação; credenciais SMTP vêm da configuração (ambiente)."""

    def __init__(self, settings):
        self.notifications = []
        self.email_host = settings.SMTP_HOST
        self.email_port = settings.SMTP_PORT
        self.email_user = settings.SMTP_USER
        self.email_password = settings.SMTP_PASSWORD

    def send_email(self, to, subject, body):
        if not self.email_user or not self.email_password:
            logger.warning("SMTP não configurado; e-mail para %s não enviado", mask_email(to))
            return False
        try:
            with smtplib.SMTP(self.email_host, self.email_port, timeout=10) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.sendmail(self.email_user, to, f"Subject: {subject}\n\n{body}")
            logger.info("E-mail enviado para %s", mask_email(to))
            return True
        except (smtplib.SMTPException, OSError) as exc:
            logger.error("Erro ao enviar e-mail para %s (%s)", mask_email(to), type(exc).__name__)
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
                f"Prioridade: {task.priority}\nStatus: {task.status}")
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': utc_now(),
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n['user_id'] == user_id]
