from utils.time import utcnow
import os
import smtplib
from datetime import datetime


class NotificationService:
    def __init__(self, config=None):
        config = config or {}
        self.notifications = []
        self.email_host = config.get('SMTP_HOST', os.environ.get('SMTP_HOST', 'smtp.gmail.com'))
        self.email_port = int(config.get('SMTP_PORT', os.environ.get('SMTP_PORT', 587)))
        self.email_user = config.get('SMTP_USER', os.environ.get('SMTP_USER', ''))
        self.email_password = config.get('SMTP_PASSWORD', os.environ.get('SMTP_PASSWORD', ''))
        self.email_from = config.get('SMTP_FROM', os.environ.get('SMTP_FROM', self.email_user))

    def send_email(self, to, subject, body):
        if not self.email_user or not self.email_password or not self.email_from:
            return False
        try:
            with smtplib.SMTP(self.email_host, self.email_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.sendmail(self.email_from, to, f"Subject: {subject}\n\n{body}")
            return True
        except (OSError, smtplib.SMTPException):
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\nPrioridade: {task.priority}\nStatus: {task.status}"
        self.send_email(user.email, subject, body)
        self.notifications.append({'type': 'task_assigned', 'user_id': user.id, 'task_id': task.id,
                                   'timestamp': utcnow()})

    def notify_task_overdue(self, user, task):
        self.send_email(user.email, f"Task atrasada: {task.title}",
                        f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}")

    def get_notifications(self, user_id):
        return [notification for notification in self.notifications if notification['user_id'] == user_id]
