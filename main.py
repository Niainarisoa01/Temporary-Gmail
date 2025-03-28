from flask import Flask, jsonify, redirect, url_for, render_template, request
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from dotenv import dotenv_values
from Helpers import Email as EmailHelper
import threading
import subprocess

config = dotenv_values(".env")

app = Flask(__name__)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["5000 per day", "50 per minute"],
    storage_uri="memory://",
)

mailbox = EmailHelper.Email()
mailbox.Login()

# Variable globale pour suivre l'état du serveur
relay_server_running = False
relay_server_process = None

# Structure de données pour stocker les messages relayés
relayed_messages = []


def index_error_responder(request_limit):
    return jsonify(
        {
            "status": "error",
            "message": "You have reached the request limit of {} requests per day".format(
                request_limit.limit
            ),
        }
    )


@app.route('/read/<email>', methods=['GET'])
@limiter.limit("20/minute", on_breach=index_error_responder)
def get_message(email):
    return jsonify(mailbox.GetMessages(email))


@app.route('/delete/<uid>', methods=['GET'])
def delete_message(uid):
    return jsonify(mailbox.delete_message(uid))


@app.route('/readby/<email>/<string_data>', methods=['GET'])
@limiter.limit("20/minute", on_breach=index_error_responder)
def read_by(email, string_data):
    if string_data is None:
        return jsonify(
            {
                'status': False,
                'message': 'Data Search is empty'
            }
        )
    else:
        return jsonify(mailbox.read_by(string_data, email))


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/api', methods=['GET'])
def api_info():
    return jsonify(
        {
            'status': True,
            'message': 'Welcome to API'
        }
    )


@app.route('/generate/<type>', methods=['GET'])
def generate_email(type):
    # Gmail Dot Trick Refrence
    #
    # https://codegolf.stackexchange.com/questions/204473/generate-gmail-dot-aliases

    return jsonify(
        {
            'status': True,
            'message': 'Success',
            'data': mailbox.generate_email(type)
        }
    )


@app.route('/relay', methods=['GET'])
def relay_interface():
    return render_template('relay.html')


@app.route('/start_relay', methods=['GET'])
def start_relay():
    global relay_server_running, relay_server_process
    
    def run_relay_server():
        subprocess.run(['python', 'relay_server.py'])
    
    # Ne démarrer que si le serveur n'est pas déjà en cours d'exécution
    if not relay_server_running:
        relay_thread = threading.Thread(target=run_relay_server)
        relay_thread.daemon = True
        relay_thread.start()
        relay_server_running = True
    
    return jsonify({
        'status': True,
        'message': 'Serveur de relais démarré'
    })


@app.route('/relay_status', methods=['GET'])
def relay_status():
    global relay_server_running
    return jsonify({
        'status': True,
        'running': relay_server_running
    })


@app.route('/read_relayed', methods=['GET'])
def read_relayed():
    from email_handler import EmailRelayHandler
    
    return jsonify({
        'status': True,
        'message': 'Messages relayés récupérés',
        'data': EmailRelayHandler.relayed_messages
    })


@app.route('/add_relayed_message', methods=['POST'])
def add_relayed_message():
    global relayed_messages
    message_data = request.get_json()
    
    # Ajouter le message à la liste
    relayed_messages.append(message_data)
    
    # Limiter à 50 messages
    if len(relayed_messages) > 50:
        relayed_messages.pop(0)
    
    return jsonify({
        'status': True,
        'message': 'Message relayé ajouté'
    })


@app.errorhandler(404)
def not_found(error):
    return redirect(url_for('index'))


# Fonction pour ajouter un message relayé
def add_relayed_message(message_data):
    global relayed_messages
    relayed_messages.append(message_data)
    # Limiter à 50 messages
    if len(relayed_messages) > 50:
        relayed_messages.pop(0)


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        threaded=True,
        debug=True
    )
