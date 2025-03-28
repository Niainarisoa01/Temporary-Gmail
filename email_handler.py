import asyncio
import smtplib
import os
from email.parser import Parser
from email.policy import default
from email.utils import formatdate
from email.message import EmailMessage
from dotenv import load_dotenv
import logging
from datetime import datetime
import requests

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

class EmailRelayHandler:
    # Ajoutez cette variable de classe pour stocker les messages
    relayed_messages = []
    
    async def handle_DATA(self, server, session, envelope):
        # Récupérer les données de l'email
        data = envelope.content.decode('utf8', errors='replace')
        
        # Utiliser le parser d'email pour traiter le message
        email_parser = Parser(policy=default)
        message = email_parser.parsestr(data)
        
        # Journaliser la réception
        logger.info(f"Email reçu de: {envelope.mail_from} pour: {envelope.rcpt_tos}")
        
        # Modifier l'email (exemple: ajouter un préfixe au sujet)
        if message.get('subject'):
            message.replace_header('subject', f"[RELAIS] {message.get('subject')}")
        else:
            message.add_header('subject', '[RELAIS] Email relayé')
            
        # Ajouter une entête personnalisée
        message.add_header('X-Relayed-By', 'Email-Relay-Service')
        
        # Ajouter la date actuelle
        if not message.get('date'):
            message.add_header('Date', formatdate())
        
        # Réacheminer l'email
        destination = os.getenv('DEFAULT_DESTINATION')
        
        # Créer un nouvel email pour le relais
        relay_message = EmailMessage()
        
        # Copier les entêtes et le contenu
        for header, value in message.items():
            if header.lower() not in ['to', 'from']:  # Ne pas copier ces entêtes
                relay_message[header] = value
        
        # Définir les nouvelles entêtes
        relay_message['From'] = envelope.mail_from
        relay_message['To'] = destination
        
        # Copier le contenu
        if message.is_multipart():
            for part in message.get_payload():
                relay_message.attach(part)
        else:
            relay_message.set_content(message.get_payload())
        
        # Stockez une copie du message relayé
        message_data = {
            'uid': str(hash(envelope.mail_from + str(datetime.now().timestamp()))),
            'from': envelope.mail_from,
            'to': destination,
            'subject': relay_message['Subject'] if 'Subject' in relay_message else '(Pas de sujet)',
            'date': formatdate(),
            'body': message.get_payload(decode=True).decode('utf-8', errors='replace') 
                 if not message.is_multipart() 
                 else "\n".join([part.get_payload(decode=True).decode('utf-8', errors='replace') 
                                for part in message.get_payload() if part.get_content_type() == 'text/plain']),
        }
        
        # Ajouter à la liste des messages relayés (limitée à 50 messages)
        self.__class__.relayed_messages.append(message_data)
        if len(self.__class__.relayed_messages) > 50:
            self.__class__.relayed_messages.pop(0)  # Supprimer le plus ancien
        
        # Envoyer l'email relayé
        try:
            await self._send_email(relay_message, destination)
            logger.info(f"Email relayé avec succès vers {destination}")
            return '250 Message accepted for relay'
        except Exception as e:
            logger.error(f"Erreur lors du relais de l'email: {str(e)}")
            return '550 Relay error'
    
    async def _send_email(self, message, destination):
        """Envoie l'email via le serveur SMTP configuré"""
        relay_host = os.getenv('RELAY_HOST')
        relay_port = int(os.getenv('RELAY_PORT'))
        relay_username = os.getenv('RELAY_USERNAME')
        relay_password = os.getenv('RELAY_PASSWORD')
        
        # Utiliser un thread pour l'envoi SMTP (bloquant)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._send_email_sync, message, 
                                   destination, relay_host, relay_port, 
                                   relay_username, relay_password)
    
    def _send_email_sync(self, message, destination, host, port, username, password):
        """Version synchrone de l'envoi d'email"""
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(message, from_addr=message['From'], to_addrs=[destination])
            logger.info(f"Email envoyé via {host}:{port}")

    def send_to_main_app(self, message_data):
        """Envoie les informations du message à l'application principale"""
        try:
            # Adresse de l'application principale
            main_app_url = "http://localhost:5000/add_relayed_message"
            requests.post(main_app_url, json=message_data)
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi au serveur principal: {str(e)}") 