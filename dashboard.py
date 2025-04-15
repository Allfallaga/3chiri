from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

# Création d'un Blueprint pour le module dashboard
dashboard_bp = Blueprint('dashboard', __name__)

# Données globales simulées
utilisateurs = {}  # Dictionnaire pour les utilisateurs
salles = {}  # Dictionnaire pour les salons
signalements = []  # Liste pour les signalements

def determiner_role_utilisateur(followers, points):
    """Détermine le rôle d'un utilisateur en fonction de ses followers et points."""
    if followers >= 1000 or points >= 1000:
        return "Influenceur"
    elif points >= 500:
        return "Contributeur"
    else:
        return "Membre"

def ajouter_transaction(username, description):
    """Ajoute une transaction au compte d'un utilisateur."""
    if username in utilisateurs:
        utilisateurs[username]['transactions'].append(description)

@dashboard_bp.route('/dashboard')
def dashboard():
    """Tableau de bord de l'utilisateur connecté."""
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder à votre tableau de bord.", 'warning')
        return redirect(url_for('connexion'))

    user = utilisateurs.get(session['username'])
    if not user:
        session.clear()
        flash("Session invalide. Veuillez vous reconnecter.", 'danger')
        return redirect(url_for('accueil'))

    return render_template('dashboard.html', user=user)

@dashboard_bp.route('/wallet/recharger', methods=['POST'])
def recharger_wallet():
    """Recharge manuelle de points pour l'utilisateur."""
    if 'username' not in session:
        flash("Veuillez vous connecter pour recharger votre portefeuille.", 'warning')
        return redirect(url_for('connexion'))

    user = utilisateurs.get(session['username'])
    if not user:
        session.clear()
        flash("Session invalide. Veuillez vous reconnecter.", 'warning')
        return redirect(url_for('accueil'))

    try:
        montant = int(request.form.get('montant', 0))
        if montant > 0:
            user['points'] += montant
            ajouter_transaction(session['username'], f"Recharge de {montant} points")
            user['role'] = determiner_role_utilisateur(user['followers'], user['points'])
            flash(f"Votre portefeuille a été rechargé de {montant} points.", 'success')
        else:
            flash("Montant invalide pour la recharge. Veuillez entrer un montant supérieur à zéro.", 'warning')
    except ValueError:
        flash("Montant invalide. Veuillez entrer un nombre entier.", 'danger')

    return redirect(url_for('dashboard'))

@dashboard_bp.route('/rooms', methods=['GET', 'POST'])
def gestion_salles():
    """Gestion des salons : création et affichage."""
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder aux salons.", 'warning')
        return redirect(url_for('connexion'))

    user = utilisateurs.get(session['username'])
    if not user:
        session.clear()
        flash("Session invalide. Veuillez vous reconnecter.", 'warning')
        return redirect(url_for('accueil'))

    if request.method == 'POST':
        nom_salle = request.form.get('nom_salle', '').strip()
        type_salle = request.form.get('type', 'public').strip()
        code_salle = request.form.get('code', '').strip()
        cost_salle = request.form.get('cost', '').strip()

        if not nom_salle:
            flash("Le nom du salon ne peut pas être vide.", 'danger')
            return redirect(url_for('dashboard.gestion_salles'))

        try:
            cost_salle = int(cost_salle) if cost_salle else 0
            if type_salle == 'payant' and cost_salle <= 0:
                cost_salle = 10  # Coût par défaut pour les salons payants
        except ValueError:
            flash("Le coût doit être un entier valide.", 'danger')
            return redirect(url_for('dashboard.gestion_salles'))

        salle_id = len(salles) + 1
        salles[salle_id] = {
            'id': salle_id,
            'nom': nom_salle,
            'type': type_salle,
            'code': code_salle if code_salle else None,
            'cost': cost_salle if type_salle == 'payant' else None,
            'messages': [],
            'participants': {},
            'banned': set()
        }

        salles[salle_id]['participants'][session['username']] = {
            'muted': False,
            'speaker': True,
            'raised_hand': False
        }

        if "Créateur de salon" not in user.get('badges', []):
            user['badges'].append("Créateur de salon")

        flash(f"Le salon '{nom_salle}' a été créé avec succès.", 'success')
        return redirect(url_for('dashboard.chat_salon', room_id=salle_id))

    return render_template('rooms.html', salles=salles, user=user)

@dashboard_bp.route('/room/<int:room_id>', methods=['GET', 'POST'])
def chat_salon(room_id):
    """Page principale d'un salon de discussion."""
    if 'username' not in session:
        flash("Connectez-vous pour rejoindre le salon.", 'warning')
        return redirect(url_for('connexion'))

    salle = salles.get(room_id)
    user = utilisateurs.get(session['username'])

    if not salle or not user:
        flash("Ce salon n'existe pas ou vous n'êtes pas connecté.", 'danger')
        return redirect(url_for('dashboard.gestion_salles'))

    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        if message and len(message) <= 300:
            salle['messages'].append({
                'author': session['username'],
                'content': message,
                'type': 'message'
            })
            flash("Message envoyé avec succès.", 'success')
        elif not message:
            flash("Le message ne peut pas être vide.", 'warning')
        else:
            flash("Message trop long (300 caractères max).", 'warning')

    return render_template('room.html', salle=salle, user=user)
