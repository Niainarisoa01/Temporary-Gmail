# Temporary Gmail

Service de messagerie temporaire et de relais d'emails.

## 🌟 Fonctionnalités

- **Consultation des emails** : Visualisez les emails reçus par adresse
- **Relais d'emails** : Redirigez les emails reçus vers une adresse permanente
- **Génération d'adresses email** : Créez des variantes d'adresses Gmail grâce au "Gmail Dot Trick"
- **API REST** : Accédez aux fonctionnalités via une API simple

## 📋 Prérequis

- Python 3.6+
- Un compte Gmail (pour le relais des emails)
- Autorisation des applications moins sécurisées sur votre compte Gmail

## 🚀 Installation

1. Clonez le dépôt
   ```bash
   git clone https://github.com/Niainarisoa01/Temporary-Gmail.git
   cd Temporary-Gmail
   ```

2. Créez un environnement virtuel
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # ou
   .venv\Scripts\activate  # Windows
   ```

3. Installez les dépendances
   ```bash
   pip install -r requirements.txt
   ```

4. Configurez le fichier `.env` avec vos identifiants Gmail
   ```
   # Email Setting
   Email=votre.email@gmail.com
   Password=votre_mot_de_passe_app
   
   # Configuration du serveur SMTP récepteur
   RECEIVING_HOST=0.0.0.0
   RECEIVING_PORT=8025
   
   # Configuration du relais SMTP sortant
   RELAY_HOST=smtp.gmail.com
   RELAY_PORT=587
   RELAY_USERNAME=votre.email@gmail.com
   RELAY_PASSWORD=votre_mot_de_passe_app
   
   # Adresse email finale de destination par défaut
   DEFAULT_DESTINATION=votre.email@gmail.com
   ```

## 🖥️ Utilisation

1. Lancez l'application
   ```bash
   python main.py
   ```

2. Accédez à l'interface web via `http://localhost:5000`

3. Pour le service de relais, accédez à `http://localhost:5000/relay`

## 🛠️ API

- **GET** `/api` - Informations sur l'API
- **GET** `/read/{email}` - Lire les messages d'une adresse email
- **GET** `/delete/{uid}` - Supprimer un message par son ID
- **GET** `/readby/{email}/{string_data}` - Rechercher des messages par contenu
- **GET** `/generate/{type}` - Générer une variante d'adresse email

## 👨‍💻 Développé par

- [@Niainarisoa01](https://github.com/Niainarisoa01)

---

# Temporary Gmail (English)

Temporary email and email relay service.

## 🌟 Features

- **Email Consultation**: View emails received by address
- **Email Relay**: Redirect received emails to a permanent address
- **Email Address Generation**: Create Gmail address variants using the "Gmail Dot Trick"
- **REST API**: Access features through a simple API

## 📋 Prerequisites

- Python 3.6+
- A Gmail account (for email relay)
- Less secure app access enabled on your Gmail account

## 🚀 Installation

1. Clone the repository
   ```bash
   git clone https://github.com/Niainarisoa01/Temporary-Gmail.git
   cd Temporary-Gmail
   ```

2. Create a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the `.env` file with your Gmail credentials
   ```
   # Email Setting
   Email=your.email@gmail.com
   Password=your_app_password
   
   # Receiving SMTP server configuration
   RECEIVING_HOST=0.0.0.0
   RECEIVING_PORT=8025
   
   # Outgoing SMTP relay configuration
   RELAY_HOST=smtp.gmail.com
   RELAY_PORT=587
   RELAY_USERNAME=your.email@gmail.com
   RELAY_PASSWORD=your_app_password
   
   # Default destination email address
   DEFAULT_DESTINATION=your.email@gmail.com
   ```

## 🖥️ Usage

1. Start the application
   ```bash
   python main.py
   ```

2. Access the web interface at `http://localhost:5000`

3. For the relay service, access `http://localhost:5000/relay`

## 🛠️ API

- **GET** `/api` - API information
- **GET** `/read/{email}` - Read messages from an email address
- **GET** `/delete/{uid}` - Delete a message by its ID
- **GET** `/readby/{email}/{string_data}` - Search messages by content
- **GET** `/generate/{type}` - Generate an email address variant

## 👨‍💻 Developed by

- [@Niainarisoa01](https://github.com/Niainarisoa01)
