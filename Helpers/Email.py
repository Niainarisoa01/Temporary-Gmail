from imap_tools import MailBox, AND
from dotenv import dotenv_values
import random
import datetime


class Email:

    def __init__(self):
        pass

    def Login(self):
        config = dotenv_values("./.env")
        mailbox = MailBox(
            host='imap.gmail.com',
            timeout=5,
        ).login(config.get("Email"), config.get("Password"))
        self.mailbox = mailbox
        self.config = config
        return mailbox

    def GetMessages(self, email):
        try:
            self.mailbox.idle.wait(timeout=3)
            data_msg = []
            for msg in self.mailbox.fetch(AND(to=email), reverse=True):
                # Assurez-vous que le corps du message est correctement extrait
                message_body = msg.text or msg.html or "(Contenu vide)"
                
                data_msg.append({
                    'to': msg.to,
                    'uid': msg.uid,
                    'from': msg.from_,
                    'date': msg.date,
                    'subject': msg.subject,
                    'body': message_body  # Utilisez le corps extrait
                })

            if not data_msg:
                return {
                    'status': False,
                    'message': 'No messages appear',
                    'email': email,
                }
            else:
                return {
                    'status': True,
                    'message': 'Messages appear',
                    'email': email,
                    'data': data_msg
                }
        except Exception as e:
            print("[ {} ] Error : {}".format(datetime.datetime.now(), e))
            self.Login()
            return {
                'status': False,
                'message': str(e),
            }

    def delete_message(self, uid):
        try:
            self.mailbox.delete(uid)
            return True
        except Exception as e:
            print(e)
            return False

    def read_by(self, string_data, email):
        data_msg = []
        for msg in self.mailbox.fetch(AND(to=email, body=string_data), reverse=True):
            data_msg.append({
                'to': msg.to,
                'uid': msg.uid,
                'from': msg.from_,
                'date': msg.date,
                'subject': msg.subject,
                'body': msg.text
            })

        if not data_msg:
            return {
                'status': False,
                'message': 'No messages appear',
                'email': email,
            }
        else:
            return {
                'status': True,
                'message': 'Messages appear',
                'email': email,
                'data': data_msg
            }

    def generate_email(self, type):
        # Nouvelle fonction qui génère des emails avec un chiffre aléatoire
        def generate_random_number_email(email, use_plus=False):
            # Générer un nombre aléatoire entre 01 et 594
            random_num = random.randint(1, 594)
            # Formater le nombre avec zéro en début si nécessaire (01, 02, etc.)
            formatted_num = f"{random_num:03d}" if random_num < 100 else str(random_num)
            
            # Pour la méthode "dot", on ajoute un point à une position aléatoire
            if not use_plus:
                chars = list(email)
                if len(chars) > 2:  # S'assurer qu'il y a assez de caractères
                    dot_position = random.randint(1, len(chars) - 1)
                    chars.insert(dot_position, '.')
                return ''.join(chars) + '@gmail.com'
            # Pour la méthode "plus", on utilise le format user+number@gmail.com
            else:
                return email + '+' + formatted_num + '@gmail.com'

        if type == "dot":
            base_email = self.config.get("Email").split("@")[0]
            data_rand = generate_random_number_email(base_email, False)
            return {
                'status': True,
                'email': data_rand,
                'mailbox': '/read/' + data_rand
            }

        elif type == "dotplus":
            base_email = self.config.get("Email").split("@")[0]
            # Utiliser la méthode + pour ajouter le nombre
            data_rand = generate_random_number_email(base_email, True)
            return {
                'status': True,
                'email': data_rand,
                'mailbox': '/read/' + data_rand
            }
