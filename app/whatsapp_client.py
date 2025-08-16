# app/whatsapp_client.py

import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

class WhatsAppClient:
    """
    Cliente para enviar mensagens via WhatsApp usando a API da Twilio.
    """
    def __init__(self):
        """
        Inicializa o cliente Twilio com as credenciais do ambiente.
        """
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([account_sid, auth_token, self.twilio_phone_number]):
            raise ValueError("As variáveis de ambiente da Twilio não estão configuradas corretamente.")
            
        self.client = Client(account_sid, auth_token)

    def send_message(self, to: str, body: str):
        """
        Envia uma mensagem de texto para um número de WhatsApp.

        Args:
            to (str): O número do destinatário no formato 'whatsapp:+55119...'
            body (str): O conteúdo da mensagem.
        """
        try:
            message = self.client.messages.create(
                from_=self.twilio_phone_number,
                body=body,
                to=to
            )
            print(f"Mensagem enviada para {to}. SID: {message.sid}")
        except TwilioRestException as e:
            print(f"Erro ao enviar mensagem para {to}: {e}")

# Instância única do cliente para ser usada em toda a aplicação
whatsapp_client = WhatsAppClient()
