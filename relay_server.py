import asyncio
import os
from aiosmtpd.controller import Controller
from email_handler import EmailRelayHandler
from dotenv import load_dotenv
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

async def start_server():
    port = int(os.getenv('RECEIVING_PORT', 8025))
    max_attempts = 5
    attempt = 0
    
    while attempt < max_attempts:
        try:
            handler = EmailRelayHandler()
            controller = Controller(
                handler, 
                hostname=os.getenv('RECEIVING_HOST', '0.0.0.0'),
                port=port
            )
            
            # Démarrer le serveur
            controller.start()
            logger.info(f"Serveur de relais démarré sur {controller.hostname}:{controller.port}")
            return controller
        except OSError as e:
            if e.errno == 98:  # Address already in use
                attempt += 1
                port += 1
                logger.warning(f"Port {port-1} déjà utilisé, tentative avec le port {port}")
            else:
                raise
    
    raise RuntimeError(f"Impossible de démarrer le serveur après {max_attempts} tentatives")

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("Arrêt du programme par l'utilisateur") 