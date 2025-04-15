from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'

utilisateurs = {}
salles = {}
signalements = []

def determiner_role_utilisateur(followers, points):
    """Détermine le rôle d'un utilisateur basé sur ses followers et points."""
    if points >= 500:
        return "Expert"
    elif points >= 200:
        return "Intermédiaire"
    else:
        return "Débutant"

def ajouter_transaction(username, description):
    """Ajoute une transaction pour un utilisateur."""
    if username in utilisateurs:
        utilisateurs[username].get('transactions', []).append(description)

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    """Page d'inscription pour un nouvel utilisateur."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        social_link = request.form.get('social_link', '').strip()
        followers = request.form.get('followers', '').strip()

        if not username or not password or not confirm:
            flash("Veuillez fournir un nom d'utilisateur, un mot de passe et une confirmation.", 'warning')
            return redirect(url_for('inscription'))
        
        if password != confirm:
            flash("Les mots de passe ne correspondent pas.", 'warning')
            return redirect(url_for('inscription'))
        
        if username in utilisateurs:
            flash("Ce nom d'utilisateur est déjà pris.", 'warning')
            return redirect(url_for('inscription'))

        try:
            followers = int(followers) if followers else 0
            if followers < 0:
                raise ValueError()
        except ValueError:
            flash("Le nombre de followers doit être un entier positif.", 'warning')
            return redirect(url_for('inscription'))

        hashed = generate_password_hash(password)
        role = determiner_role_utilisateur(followers, 0)
        utilisateurs[username] = {
            'username': username,
            'password_hash': hashed,
            'followers': followers,
            'social_link': social_link,
            'is_admin': False,
            'role': role,
            'points': 100,
            'badges': [],
            'transactions': []
        }

        utilisateurs[username]['badges'].append("Nouvel utilisateur")
        ajouter_transaction(username, "Points initiaux : +100")

        if len(utilisateurs) == 1:
            utilisateurs[username]['is_admin'] = True
            flash("Vous êtes désigné administrateur en tant que premier utilisateur inscrit.", 'info')

        session['username'] = username
        flash(f"Inscription réussie. Bienvenue, {username} !", 'success')
        return redirect(url_for('dashboard'))

    return render_template('inscription.html')

@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    """Page de connexion pour un utilisateur existant."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if username in utilisateurs and check_password_hash(utilisateurs[username]['password_hash'], password):
            session['username'] = username
            flash("Connexion réussie.", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", 'danger')

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

    user = utilisateurs.get(session['username'])
    return render_template('dashboard.html', user=user)

@app.route('/wallet/recharger', methods=['POST'])
def recharger_wallet():
    """Recharge manuelle de points pour l'utilisateur."""
    if 'username' not in session:
        flash("Veuillez vous connecter pour recharger votre portefeuille.", 'warning')
        return redirect(url_for('connexion'))

    user = utilisateurs.get(session['username'])
    if not user:
        session.clear()
        flash("Session invalide, veuillez vous reconnecter.", 'warning')
        return redirect(url_for('accueil'))

    try:
        montant = int(request.form.get('montant', 0))
        if montant > 0:
            user['points'] += montant
            ajouter_transaction(session['username'], f"Recharge de {montant} points")
            flash(f"Votre portefeuille a été rechargé de {montant} points.", 'success')
            user['role'] = determiner_role_utilisateur(user['followers'], user['points'])
        else:
            flash("Montant invalide pour la recharge. Veuillez entrer un montant supérieur à zéro.", 'warning')
    except ValueError:
        flash("Montant invalide. Veuillez entrer un nombre entier.", 'danger')

    return redirect(url_for('dashboard'))

# Ajouter d'autres routes et fonctions si nécessaire...

if __name__ == '__main__':
    app.run(debug=True)
