@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    """Page d'inscription pour un nouvel utilisateur."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        social_link = request.form.get('social_link', '').strip()
        followers = request.form.get('followers', '').strip()

        # Validation des champs requis
        if not username or not password or not confirm:
            flash("Veuillez fournir un nom d'utilisateur, un mot de passe et une confirmation.", 'warning')
            return redirect(url_for('inscription'))
        
        if password != confirm:
            flash("Les mots de passe ne correspondent pas.", 'warning')
            return redirect(url_for('inscription'))
        
        if username in utilisateurs:
            flash("Ce nom d'utilisateur est déjà pris.", 'warning')
            return redirect(url_for('inscription'))

        # Vérification si le nombre de followers est un entier positif
        try:
            followers = int(followers) if followers else 0
            if followers < 0:
                raise ValueError()
        except ValueError:
            flash("Le nombre de followers doit être un entier positif.", 'warning')
            return redirect(url_for('inscription'))

        # Création du nouvel utilisateur avec un hash sécurisé
        hashed = generate_password_hash(password)
        role = determiner_role_utilisateur(followers, 0)
        utilisateurs[username] = {
            'username': username,
            'password_hash': hashed,
            'followers': followers,
            'social_link': social_link,
            'is_admin': False,
            'role': role,
            'points': 100,  # Points de départ
            'badges': [],
            'transactions': []
        }

        # Ajouter un badge d'inscription
        utilisateurs[username]['badges'].append("Nouvel utilisateur")
        # Enregistrer la transaction initiale
        ajouter_transaction(username, "Points initiaux : +100")

        # Premier utilisateur inscrit devient administrateur
        if len(utilisateurs) == 1:
            utilisateurs[username]['is_admin'] = True
            flash("Vous êtes désigné administrateur en tant que premier utilisateur inscrit.", 'info')

        # Connexion automatique après inscription
        session['username'] = username
        flash(f"Inscription réussie. Bienvenue, {username} !", 'success')
        return redirect(url_for('dashboard'))

    # Afficher le formulaire d'inscription
    return render_template('inscription.html')


@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    """Page de connexion pour un utilisateur existant."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Validation des identifiants
        if username in utilisateurs and check_password_hash(utilisateurs[username]['password_hash'], password):
            session['username'] = username
            flash("Connexion réussie.", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", 'danger')

    # GET : Afficher le formulaire de connexion
    return render_template('connexion.html')


@app.route('/deconnexion')
def deconnexion():
    """Déconnexion de l'utilisateur courant."""
    session.clear()
    flash("Vous avez été déconnecté.", 'info')
    return redirect(url_for('accueil'))


@app.route('/dashboard')
def dashboard():
    """Tableau de bord de l'utilisateur connecté."""
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder à votre tableau de bord.", 'warning')
        return redirect(url_for('connexion'))

    return render_template('dashboard.html')


@app.route('/wallet/recharger', methods=['POST'])
def recharger_wallet():
    """Recharge manuelle de points pour l'utilisateur."""
    # Vérifier si l'utilisateur est connecté
    if 'username' not in session:
        flash("Veuillez vous connecter pour recharger votre portefeuille.", 'warning')
        return redirect(url_for('connexion'))

    # Récupérer les informations de l'utilisateur
    user = utilisateurs.get(session['username'])
    if not user:
        # Cas improbable : l'utilisateur en session n'existe pas
        session.clear()
        flash("Session invalide, veuillez vous reconnecter.", 'warning')
        return redirect(url_for('accueil'))

    try:
        # Récupérer et valider le montant saisi
        montant = int(request.form.get('montant', 0))
        if montant > 0:
            # Ajouter les points et mettre à jour le rôle
            user['points'] += montant
            ajouter_transaction(session['username'], f"Recharge de {montant} points")
            flash(f"Votre portefeuille a été rechargé de {montant} points.", 'success')

            # Mise à jour du rôle de l'utilisateur en fonction des points
            user['role'] = determiner_role_utilisateur(user['followers'], user['points'])
        else:
            # Gérer un montant invalide
            flash("Montant invalide pour la recharge. Veuillez entrer un montant supérieur à zéro.", 'warning')
    except ValueError:
        # Gestion d'une saisie invalide
        flash("Montant invalide. Veuillez entrer un nombre entier.", 'danger')

    return redirect(url_for('dashboard'))

return redirect(url_for('dashboard'))


@app.route('/rooms', methods=['GET', 'POST'])
def gestion_salles():
    """Liste des salons existants et création d'une nouvelle salle."""
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder aux salons.", 'warning')
        return redirect(url_for('connexion'))

    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        type_salle = request.form.get('type', '').strip()
        code = request.form.get('code', '').strip()
        cost = request.form.get('cost', '').strip()

        # Validation des champs
        if not nom:
            flash("Le nom de la salle est requis.", 'warning')
            return redirect(url_for('gestion_salles'))

        try:
            cost = int(cost) if cost else 0
            if type_salle == 'payant' and cost <= 0:
                cost = 10  # Coût par défaut pour les salles payantes
        except ValueError:
            flash("Le coût doit être un nombre entier valide.", 'warning')
            return redirect(url_for('gestion_salles'))

        # Création d'un nouvel identifiant de salle
        salle_id = len(salles) + 1
        salles[salle_id] = {
            'id': salle_id,
            'nom': nom,
            'type': type_salle,
            'owner': session['username'],
            'code': code if code else None,
            'cost': cost if type_salle == 'payant' else None,
            'participants': {},
            'messages': [],
            'banned': set()
        }

        # Le créateur rejoint automatiquement la salle comme conférencier
        salles[salle_id]['participants'][session['username']] = {
            'muted': False,
            'speaker': True,
            'raised_hand': False
        }

        flash(f"Le salon '{nom}' a été créé avec succès.", 'success')

        # Ajouter un badge pour la création de la première salle
        user = utilisateurs.get(session['username'])
        if user and "Créateur de salon" not in user['badges']:
            user['badges'].append("Créateur de salon")

        return redirect(url_for('chat_salon', room_id=salle_id))

    # GET : Afficher la liste des salons et le formulaire de création
    return render_template('rooms.html', salles=salles, user=utilisateurs.get(session['username']))


@app.route('/room/<int:room_id>', methods=['GET', 'POST'])
def chat_salon(room_id):
    """Page principale d'un salon de discussion, avec chat et actions en temps réel."""
    if 'username' not in session:
        flash("Connectez-vous pour rejoindre le salon.", 'warning')
        return redirect(url_for('connexion'))

    if room_id not in salles:
        flash("Ce salon n'existe pas.", 'danger')
        return redirect(url_for('gestion_salles'))

    # Charger les informations de la salle
    salle = salles[room_id]
    user = utilisateurs.get(session['username'])

    if not user:
        # Gérer le cas où l'utilisateur en session est introuvable
        flash("Erreur : utilisateur introuvable.", 'danger')
        return redirect(url_for('accueil'))
       # Cas improbable : l'utilisateur en session n'existe plus
session.clear()
flash("Session invalide, veuillez vous reconnecter.", 'warning')
return redirect(url_for('accueil'))


# Route pour créer un salon ou afficher la liste des salons existants
@app.route('/rooms', methods=['GET', 'POST'])
def gestion_salles():
    """Gestion des salons : création et affichage."""
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder aux salons.", 'warning')
        return redirect(url_for('connexion'))

    # Vérification de l'utilisateur en session
    user = utilisateurs.get(session['username'])
    if not user:
        session.clear()
        flash("Session invalide, veuillez vous reconnecter.", 'warning')
        return redirect(url_for('accueil'))

    if request.method == 'POST':
        # Création d'un salon
        nom_salle = request.form.get('nom_salle', '').strip()
        type_salle = request.form.get('type', 'public').strip()
        code_salle = request.form.get('code', '').strip()
        cost_salle = request.form.get('cost', '').strip()

        # Validation du nom de salle
        if not nom_salle:
            flash("Le nom du salon ne peut pas être vide.", 'danger')
            return redirect(url_for('gestion_salles'))

        try:
            # Validation et conversion du coût
            cost_salle = int(cost_salle) if cost_salle else 0
            if type_salle == 'payant' and cost_salle <= 0:
                cost_salle = 10  # Coût par défaut pour les salles payantes
        except ValueError:
            flash("Le coût doit être un entier valide.", 'danger')
            return redirect(url_for('gestion_salles'))

        # Création de la salle
        salle_id = len(salles) + 1
        salles[salle_id] = {
            'id': salle_id,
            'nom': nom_salle,
            'type': type_salle,
            'code': code_salle if code_salle else None,
            'cost': cost_salle if type_salle == 'payant' else None,
            'messages': [],
            'participants': {},
            'banned': set()  # Utilisation de set pour les bannis pour éviter les doublons
        }

        # Ajouter le créateur comme participant principal
        salles[salle_id]['participants'][session['username']] = {
            'muted': False,
            'speaker': True,
            'raised_hand': False
        }

        flash(f"Le salon '{nom_salle}' a été créé avec succès.", 'success')

        # Ajouter un badge pour la création de la première salle
        if user and "Créateur de salon" not in user.get('badges', []):
            user['badges'].append("Créateur de salon")

        return redirect(url_for('chat_salon', room_id=salle_id))

    # GET : Afficher la liste des salons et le formulaire de création
    return render_template('rooms.html', salles=salles, user=user)

# Route pour gérer la page d'un salon
@app.route('/room/<int:room_id>', methods=['GET', 'POST'])
def chat_salon(room_id):
    """Page principale d'un salon de discussion, avec chat et actions en temps réel."""
    if 'username' not in session:
        flash("Connectez-vous pour rejoindre le salon.", 'warning')
        return redirect(url_for('connexion'))

    if room_id not in salles:
        flash("Ce salon n'existe pas.", 'danger')
        return redirect(url_for('gestion_salles'))

    # Charger les informations de la salle
    salle = salles.get(room_id)
    user = utilisateurs.get(session['username'])

    if not user:
        # Cas improbable : utilisateur introuvable
        session.clear()
        flash("Session invalide, veuillez vous reconnecter.", 'warning')
        return redirect(url_for('accueil'))

    if request.method == 'POST':
        # Vérifier l'action demandée
        action = request.form.get('action', '').strip()

        if action == 'enter':
            # Gérer l'accès au salon (privé ou payant)
            if salle['type'] == 'prive':
                code_fourni = request.form.get('code', '').strip()
                if salle.get('code') and code_fourni != salle['code']:
                    flash("Code d'accès incorrect.", 'danger')
                    return redirect(url_for('gestion_salles'))

            if salle['type'] == 'payant':
                cost = salle.get('cost', 0)
                if user['points'] < cost:
                    flash("Points insuffisants pour rejoindre ce salon payant.", 'danger')
                    return redirect(url_for('gestion_salles'))
                else:
                    # Déduire les points et enregistrer la transaction
                    user['points'] -= cost
                    ajouter_transaction(session['username'], f"Accès au salon payant '{salle['nom']}': -{cost} points")
                    flash(f"{cost} points ont été débités pour accéder au salon payant.", 'info')

            # Ajouter l'utilisateur comme participant
            if session['username'] not in salle['participants']:
                salle['participants'][session['username']] = {'muted': False, 'speaker': False, 'raised_hand': False}

            flash(f"Vous avez rejoint le salon '{salle['nom']}'.", 'success')
            return redirect(url_for('chat_salon', room_id=room_id))

        if action == 'send':
            # Gérer l'envoi de messages
            message = request.form.get('message', '').strip()
            if message:
                participant = salle['participants'].get(session['username'])
                if participant and participant.get('muted'):
                    flash("Vous êtes muet et ne pouvez pas envoyer de message.", 'warning')
                elif len(message) > 300:
                    flash("Message trop long (300 caractères max).", 'warning')
                else:
                    # Ajouter le message à l'historique
                    salle['messages'].append({
                        'author': session['username'],
                        'content': message,
                        'type': 'message'
                    })
                    # Ajouter un badge pour le premier message
                    if user and "Premiers pas" not in user.get('badges', []):
                        user['badges'].append("Premiers pas")
                    flash("Message envoyé avec succès.", 'success')
            else:
                flash("Le message ne peut pas être vide.", 'warning')

    return render_template('room.html', salle=salle, user=user)

 # Gestion de la levée ou baisse de la main
if username in salle['participants']:
    participant = salle['participants'][username]
    if not participant.get('speaker', False):  # Vérifie si le participant n'est pas conférencier
        # Basculer l'état de la main levée
        participant['raised_hand'] = not participant.get('raised_hand', False)
        action_text = "a levé la main" if participant['raised_hand'] else "a baissé la main"
        # Ajouter un message d'action dans le salon
        salle['messages'].append({'author': username, 'content': action_text, 'type': 'action'})
        flash(f"Votre main a été {'levée' if participant['raised_hand'] else 'baissée'}.", 'info')
    else:
        flash("Vous êtes conférencier, cette action n'est pas nécessaire.", 'warning')  # Message clair pour les conférenciers
else:
    flash("Vous n'êtes pas un participant de ce salon.", 'danger')

return redirect(url_for('chat_salon', room_id=room_id))


# Gestion de l'activation/désactivation du micro
@app.route('/toggle_mic/<int:room_id>', methods=['POST'])
def basculer_micro(room_id):
    """Permet à un conférencier d'activer ou de désactiver son micro."""
    if 'username' not in session:
        flash("Vous devez être connecté pour effectuer cette action.", 'warning')
        return redirect(url_for('connexion'))
    
    salle = salles.get(room_id)
    if not salle:
        flash("Ce salon n'existe pas.", 'danger')
        return redirect(url_for('rooms'))
    
    username = session['username']
    participant = salle['participants'].get(username)

    if not participant:
        flash("Vous n'êtes pas un participant de ce salon.", 'danger')
        return redirect(url_for('rooms'))

    if not participant.get('speaker', False):  # Vérifie si l'utilisateur est un conférencier
        flash("Vous devez être conférencier pour activer ou désactiver votre micro.", 'danger')
        return redirect(url_for('chat_salon', room_id=room_id))

    # Basculer l'état du micro
    participant['muted'] = not participant.get('muted', True)
    action_text = "a coupé son micro" if participant['muted'] else "a réactivé son micro"
    salle['messages'].append({'author': username, 'content': action_text, 'type': 'action'})
    flash(f"Votre micro a été {'désactivé' if participant['muted'] else 'activé'}.", 'info')
    
    return redirect(url_for('chat_salon', room_id=room_id))


# Gestion de l'expulsion d'un utilisateur
@app.route('/kick/<int:room_id>/<target>', methods=['POST'])
def expulser(room_id, target):
    """Permet au propriétaire ou à un administrateur d'expulser un utilisateur d'un salon."""
    if 'username' not in session:
        flash("Vous devez être connecté pour effectuer cette action.", 'warning')
        return redirect(url_for('connexion'))
    
    salle = salles.get(room_id)
    if not salle:
        flash("Ce salon n'existe pas.", 'danger')
        return redirect(url_for('rooms'))

    username = session['username']

    # Vérifier les permissions
    if username == salle['owner'] or utilisateurs.get(username, {}).get('is_admin'):
        if target in salle['participants']:
            # Expulsion de l'utilisateur
            salle['participants'].pop(target, None)
            salle['banned'].add(target)
            salle['messages'].append({'author': username, 'content': f"{target} a été expulsé.", 'type': 'action'})
            flash(f"{target} a été expulsé du salon.", 'info')
        else:
            flash("L'utilisateur n'est pas présent dans ce salon.", 'warning')
    else:
        flash("Vous n'avez pas les permissions pour expulser un utilisateur.", 'danger')

    return redirect(url_for('chat_salon', room_id=room_id))


# Gestion du mute/unmute d'un utilisateur
@app.route('/mute/<int:room_id>/<target>', methods=['POST'])
def mute(room_id, target):
    """Permet au propriétaire ou à un administrateur de rendre muet ou de réactiver un utilisateur."""
    if 'username' not in session:
        flash("Vous devez être connecté pour effectuer cette action.", 'warning')
        return redirect(url_for('connexion'))
    
    salle = salles.get(room_id)
    if not salle:
        flash("Ce salon n'existe pas.", 'danger')
        return redirect(url_for('rooms'))

    username = session['username']

    # Vérifier les permissions
    if username == salle['owner'] or utilisateurs.get(username, {}).get('is_admin', False):
        participant = salle['participants'].get(target)
        if participant:
            # Basculer l'état mute
            participant['muted'] = not participant.get('muted', False)
            action_text = f"{target} a été {'rendu muet' if participant['muted'] else 'réactivé'}."
            salle['messages'].append({'author': username, 'content': action_text, 'type': 'action'})
            flash(f"{target} a été {'rendu muet' if participant['muted'] else 'réactivé'}.", 'info')
        else:
            flash("L'utilisateur n'est pas un participant de ce salon.", 'warning')
    else:
        flash("Vous n'avez pas les permissions pour rendre muet ou réactiver un utilisateur.", 'danger')

    return redirect(url_for('chat_salon', room_id=room_id))
    
   # Gestion de l'état muet d'un utilisateur
def basculer_muet(room_id, target):
    """Permet au propriétaire ou à un administrateur de rendre muet ou de réactiver un utilisateur."""
    if 'username' not in session:
        flash("Vous devez être connecté pour effectuer cette action.", 'warning')
        return redirect(url_for('connexion'))

    salle = salles.get(room_id)
    if not salle:
        flash("Ce salon n'existe pas.", 'danger')
        return redirect(url_for('rooms'))

    username = session['username']

    # Vérifier les permissions
    if username == salle['owner'] or utilisateurs.get(username, {}).get('is_admin', False):
        participant = salle['participants'].get(target)
        if participant:
            # Basculer l'état muet
            participant['muted'] = not participant.get('muted', False)
            etat = "muet" if participant['muted'] else "audible"
            salle['messages'].append({'author': username, 'content': f"{target} est maintenant {etat}.", 'type': 'action'})
            flash(f"L'état muet de {target} a été basculé à {etat}.", 'info')
        else:
            flash("L'utilisateur n'est pas un participant de ce salon.", 'warning')
    else:
        flash("Vous n'avez pas les permissions pour rendre un utilisateur muet.", 'danger')

    return redirect(url_for('chat_salon', room_id=room_id))


@app.route('/make_speaker/<int:room_id>/<target>', methods=['POST'])
def donner_micro(room_id, target):
    """Permet au propriétaire ou à un administrateur de donner la parole à un utilisateur ayant levé la main."""
    if 'username' not in session:
        flash("Vous devez être connecté pour effectuer cette action.", 'warning')
        return redirect(url_for('connexion'))

    salle = salles.get(room_id)
    if not salle:
        flash("Ce salon n'existe pas.", 'danger')
        return redirect(url_for('rooms'))

    username = session['username']

    # Vérifier les permissions
    if username == salle['owner'] or utilisateurs.get(username, {}).get('is_admin', False):
        participant = salle['participants'].get(target)
        if participant and participant.get('raised_hand', False):
            # Donner la parole
            participant['raised_hand'] = False
            participant['speaker'] = True
            participant['muted'] = False  # Déverrouiller le micro par défaut
            salle['messages'].append({'author': username, 'content': f"{target} peut maintenant parler.", 'type': 'action'})
            flash(f"{target} est désormais conférencier.", 'info')
        else:
            flash("L'utilisateur n'a pas levé la main ou n'est pas un participant.", 'warning')
    else:
        flash("Vous n'avez pas les permissions pour donner la parole.", 'danger')

    return redirect(url_for('chat_salon', room_id=room_id))


@app.route('/report/<int:room_id>/<target>', methods=['POST'])
def signaler(room_id, target):
    """Permet de signaler un utilisateur pour abus."""
    if 'username' not in session:
        flash("Vous devez être connecté pour effectuer cette action.", 'warning')
        return redirect(url_for('connexion'))
    
    salle = salles.get(room_id)
    if not salle or target not in salle['participants']:
        flash("Ce salon ou cet utilisateur n'existe pas.", 'danger')
        return redirect(url_for('rooms'))

    # Enregistrer le signalement
    signalements.append({'de': session['username'], 'cible': target, 'salle': room_id})
    flash(f"Le comportement de {target} a été signalé aux modérateurs.", 'info')
    return redirect(url_for('chat_salon', room_id=room_id))
