document.addEventListener('DOMContentLoaded', function() {
    let currentEmail = localStorage.getItem('tempEmail') || '';
    const emailDisplay = document.getElementById('email-address');
    const copyButton = document.getElementById('copy-email');
    const generateDotBtn = document.getElementById('generate-dot');
    const generateDotPlusBtn = document.getElementById('generate-dotplus');
    const refreshBtn = document.getElementById('refresh-inbox');
    const messagesList = document.getElementById('messages-list');
    const messageView = document.getElementById('message-view');
    const searchInput = document.getElementById('search-input');
    const noMessages = document.getElementById('no-messages');
    const loadingIndicator = document.getElementById('loading');
    const normalTab = document.getElementById('normal-tab');
    const relayedTab = document.getElementById('relayed-tab');
    let currentTab = 'normal';
    
    // Initialiser l'interface
    if (currentEmail) {
        emailDisplay.textContent = currentEmail;
        fetchMessages(currentEmail);
    } else {
        showNoMessages("Générez une adresse email temporaire pour commencer");
    }
    
    // Copier l'email au presse-papier
    copyButton.addEventListener('click', function() {
        if (currentEmail) {
            navigator.clipboard.writeText(currentEmail)
                .then(() => {
                    copyButton.textContent = 'Copié!';
                    setTimeout(() => {
                        copyButton.textContent = 'Copier';
                    }, 2000);
                })
                .catch(err => {
                    console.error('Erreur de copie: ', err);
                });
        }
    });
    
    // Générer une adresse email temporaire avec "dot"
    generateDotBtn.addEventListener('click', function() {
        showLoading();
        fetch('/generate/dot')
            .then(response => response.json())
            .then(data => {
                if (data.status) {
                    currentEmail = data.data.email;
                    emailDisplay.textContent = currentEmail;
                    localStorage.setItem('tempEmail', currentEmail);
                    fetchMessages(currentEmail);
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                hideLoading();
            });
    });
    
    // Générer une adresse email temporaire avec "dotplus"
    generateDotPlusBtn.addEventListener('click', function() {
        showLoading();
        fetch('/generate/dotplus')
            .then(response => response.json())
            .then(data => {
                if (data.status) {
                    currentEmail = data.data.email;
                    emailDisplay.textContent = currentEmail;
                    localStorage.setItem('tempEmail', currentEmail);
                    fetchMessages(currentEmail);
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                hideLoading();
            });
    });
    
    // Rafraîchir les messages
    refreshBtn.addEventListener('click', function() {
        if (currentTab === 'normal' && currentEmail) {
            fetchMessages(currentEmail);
        } else if (currentTab === 'relayed') {
            fetchRelayedMessages();
        }
    });
    
    // Rechercher dans l'inbox
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.trim();
        if (currentEmail && searchTerm.length > 0) {
            searchMessages(currentEmail, searchTerm);
        } else if (currentEmail) {
            fetchMessages(currentEmail);
        }
    });
    
    // Fonction pour récupérer les messages
    function fetchMessages(email) {
        showLoading();
        messageView.classList.add('hidden');
        
        fetch(`/read/${email}`)
            .then(response => response.json())
            .then(data => {
                hideLoading();
                if (data.status && data.data && data.data.length > 0) {
                    renderMessages(data.data);
                } else {
                    showNoMessages("Aucun message pour le moment. Les messages apparaîtront ici.");
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                hideLoading();
                showNoMessages("Erreur lors du chargement des messages.");
            });
    }
    
    // Fonction pour rechercher des messages
    function searchMessages(email, searchTerm) {
        showLoading();
        messageView.classList.add('hidden');
        
        fetch(`/readby/${email}/${searchTerm}`)
            .then(response => response.json())
            .then(data => {
                hideLoading();
                if (data.status && data.data && data.data.length > 0) {
                    renderMessages(data.data);
                } else {
                    showNoMessages(`Aucun message contenant "${searchTerm}"`);
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                hideLoading();
                showNoMessages("Erreur lors de la recherche.");
            });
    }
    
    // Fonction pour afficher les messages
    function renderMessages(messages) {
        messagesList.innerHTML = '';
        noMessages.classList.add('hidden');
        messagesList.classList.remove('hidden');
        
        messages.forEach(message => {
            const li = document.createElement('li');
            li.className = 'message-item';
            li.dataset.uid = message.uid;
            
            const date = new Date(message.date);
            const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
            
            li.innerHTML = `
                <h3>${message.subject || '(Pas de sujet)'}</h3>
                <div class="message-meta">
                    <span>De: ${message.from}</span>
                    <span>${formattedDate}</span>
                </div>
            `;
            
            li.addEventListener('click', function() {
                viewMessage(message);
            });
            
            messagesList.appendChild(li);
        });
    }
    
    // Fonction pour afficher un message
    function viewMessage(message) {
        messageView.classList.remove('hidden');
        
        const date = new Date(message.date);
        const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        
        // Échapper le HTML dans le corps du message pour éviter les injections XSS
        const safeBody = message.body 
            ? message.body.replace(/</g, '&lt;').replace(/>/g, '&gt;') 
            : '(Pas de contenu)';
        
        messageView.innerHTML = `
            <div class="message-header">
                <h2>${message.subject || '(Pas de sujet)'}</h2>
                <div class="message-info">
                    <div>De: ${message.from}</div>
                    <div>Date: ${formattedDate}</div>
                </div>
            </div>
            <div class="message-content">${safeBody}</div>
            <div style="margin-top: 20px;">
                <button class="btn btn-danger" id="delete-message">Supprimer</button>
            </div>
        `;
        
        document.getElementById('delete-message').addEventListener('click', function() {
            deleteMessage(message.uid);
        });
    }
    
    // Fonction pour supprimer un message
    function deleteMessage(uid) {
        if (confirm('Êtes-vous sûr de vouloir supprimer ce message?')) {
            fetch(`/delete/${uid}`)
                .then(response => response.json())
                .then(result => {
                    if (result === true) {
                        messageView.classList.add('hidden');
                        if (currentEmail) {
                            fetchMessages(currentEmail);
                        }
                    }
                })
                .catch(error => {
                    console.error('Erreur:', error);
                });
        }
    }
    
    // Afficher le message "Aucun message"
    function showNoMessages(message) {
        noMessages.textContent = message || "Aucun message";
        noMessages.classList.remove('hidden');
        messagesList.classList.add('hidden');
    }
    
    // Afficher l'indicateur de chargement
    function showLoading() {
        loadingIndicator.classList.remove('hidden');
        messagesList.classList.add('hidden');
        noMessages.classList.add('hidden');
    }
    
    // Masquer l'indicateur de chargement
    function hideLoading() {
        loadingIndicator.classList.add('hidden');
    }
    
    // Fonction pour récupérer les messages relayés
    function fetchRelayedMessages() {
        showLoading();
        messageView.classList.add('hidden');
        
        fetch('/read_relayed')
            .then(response => response.json())
            .then(data => {
                hideLoading();
                if (data.status && data.data && data.data.length > 0) {
                    renderMessages(data.data);
                } else {
                    showNoMessages("Aucun message relayé pour le moment.");
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                hideLoading();
                showNoMessages("Erreur lors du chargement des messages relayés.");
            });
    }
    
    // Ajoutez les gestionnaires d'événements pour les onglets
    normalTab.addEventListener('click', function() {
        normalTab.classList.add('active');
        relayedTab.classList.remove('active');
        currentTab = 'normal';
        if (currentEmail) {
            fetchMessages(currentEmail);
        } else {
            showNoMessages("Générez une adresse email temporaire pour commencer");
        }
    });
    
    relayedTab.addEventListener('click', function() {
        relayedTab.classList.add('active');
        normalTab.classList.remove('active');
        currentTab = 'relayed';
        fetchRelayedMessages();
    });
}); 