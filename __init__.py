from flask import Blueprint, request, session, flash, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash

# Définir un Blueprint pour les routes
routes = Blueprint('routes', __name__)

# Exemple de stockage en mémoire pour les utilisateurs et les salles
utilisateurs = {}
salles = {}

# Route pour l'inscription
@routes.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not username or not password or not confirm:
            flash("Veuillez compléter tous les champs.", "warning")
            return redirect(url_for('routes.inscription'))

        if password != confirm:
            flash("Les mots de passe ne correspondent pas.", "warning")
            return redirect(url_for('routes.inscription'))

        if username in utilisateurs:
            flash("Ce nom d'utilisateur est déjà pris.", "warning")
            return redirect(url_for('routes.inscription'))

        utilisateurs[username] = {
            'username': username,
            'password_hash': generate_password_hash(password),
            'is_admin': False,
        }

        if len(utilisateurs) == 1:
            utilisateurs[username]['is_admin'] = True
            flash("Vous êtes le premier utilisateur et administrateur.", "info")

        session['username'] = username
        flash("Inscription réussie.", "success")
        return redirect(url_for('routes.dashboard'))

    return render_template('inscription.html')

# Route pour la connexion
@routes.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if username in utilisateurs and check_password_hash(utilisateurs[username]['password_hash'], password):
            session['username'] = username
            flash("Connexion réussie.", "success")
            return redirect(url_for('routes.dashboard'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", "danger")

    return render_template('connexion.html')

# Route pour le tableau de bord
@routes.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder à votre tableau de bord.", "warning")
        return redirect(url_for('routes.connexion'))
    return render_template('dashboard.html', user=utilisateurs.get(session['username']))

# Route pour gérer les salles
@routes.route('/rooms', methods=['GET', 'POST'])
def gestion_salles():
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder aux salons.", "warning")
        return redirect(url_for('routes.connexion'))

    user = utilisateurs.get(session['username'])
    if not user:
        session.clear()
        flash("Session invalide, veuillez vous reconnecter.", "warning")
        return redirect(url_for('routes.inscription'))

    if request.method == 'POST':
        nom_salle = request.form.get('nom', '').strip()
        type_salle = request.form.get('type', 'public').strip()
        cost_salle = request.form.get('cost', '').strip()

        if not nom_salle:
            flash("Le nom de la salle est requis.", "warning")
            return redirect(url_for('routes.gestion_salles'))

        try:
            cost_salle = int(cost_salle) if cost_salle else 0
        except ValueError:
            flash("Le coût doit être un nombre entier.", "warning")
            return redirect(url_for('routes.gestion_salles'))

        salle_id = len(salles) + 1
        salles[salle_id] = {
            'id': salle_id,
            'nom': nom_salle,
            'type': type_salle,
            'cost': cost_salle,
            'participants': [],
        }

        flash(f"Salle '{nom_salle}' créée avec succès.", "success")
        return redirect(url_for('routes.gestion_salles'))

    return render_template('rooms.html', salles=salles)

# Ajoutez d'autres routes comme /room/<id>, /kick, etc., ici...
