
from flask import Flask, request, session, redirect, url_for, flash, render_template

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Simulated data
utilisateurs = {}
salles = {}
signalements = []

# Route: Create or display list of rooms
@app.route('/rooms', methods=['GET', 'POST'])
def gestion_salles():
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder aux salons.", 'warning')
        return redirect(url_for('connexion'))

    user = utilisateurs.get(session['username'])
    if not user:
        session.clear()
        flash("Session invalide, veuillez vous reconnecter.", 'warning')
        return redirect(url_for('accueil'))

    if request.method == 'POST':
        nom_salle = request.form.get('nom_salle', '').strip()
        type_salle = request.form.get('type', 'public').strip()
        code_salle = request.form.get('code', '').strip()
        cost_salle = request.form.get('cost', '').strip()

        if not nom_salle:
            flash("Le nom du salon ne peut pas être vide.", 'danger')
            return redirect(url_for('gestion_salles'))

        try:
            cost_salle = int(cost_salle) if cost_salle else 0
            if type_salle == 'payant' and cost_salle <= 0:
                cost_salle = 10
        except ValueError:
            flash("Le coût doit être un entier valide.", 'danger')
            return redirect(url_for('gestion_salles'))

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

        if user and "Créateur de salon" not in user.get('badges', []):
            user['badges'].append("Créateur de salon")

        flash(f"Le salon '{nom_salle}' a été créé avec succès.", 'success')
        return redirect(url_for('chat_salon', room_id=salle_id))

    return render_template('rooms.html', salles=salles, user=user)

# Route: Chat room page
@app.route('/room/<int:room_id>', methods=['GET', 'POST'])
def chat_salon(room_id):
    if 'username' not in session:
        flash("Connectez-vous pour rejoindre le salon.", 'warning')
        return redirect(url_for('connexion'))

    salle = salles.get(room_id)
    if not salle:
        flash("Ce salon n'existe pas.", 'danger')
        return redirect(url_for('gestion_salles'))

    user = utilisateurs.get(session['username'])
    if not user:
        session.clear()
        flash("Session invalide, veuillez vous reconnecter.", 'warning')
        return redirect(url_for('accueil'))

    if request.method == 'POST':
        action = request.form.get('action', '').strip()

        if action == 'enter':
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
                    user['points'] -= cost
                    flash(f"{cost} points ont été débités pour accéder au salon payant.", 'info')

            if session['username'] not in salle['participants']:
                salle['participants'][session['username']] = {'muted': False, 'speaker': False, 'raised_hand': False}

            flash(f"Vous avez rejoint le salon '{salle['nom']}'.", 'success')

        elif action == 'send':
            message = request.form.get('message', '').strip()
            if message:
                participant = salle['participants'].get(session['username'])
                if participant and participant.get('muted'):
                    flash("Vous êtes muet et ne pouvez pas envoyer de message.", 'warning')
                elif len(message) > 300:
                    flash("Message trop long (300 caractères max).", 'warning')
                else:
                    salle['messages'].append({
                        'author': session['username'],
                        'content': message,
                        'type': 'message'
                    })
                    flash("Message envoyé avec succès.", 'success')

    return render_template('room.html', salle=salle, user=user)

# Route: Mute/unmute a user
@app.route('/mute/<int:room_id>/<target>', methods=['POST'])
def mute(room_id, target):
    if 'username' not in session:
        flash("Vous devez être connecté pour effectuer cette action.", 'warning')
        return redirect(url_for('connexion'))

    salle = salles.get(room_id)
    if not salle:
        flash("Ce salon n'existe pas.", 'danger')
        return redirect(url_for('rooms'))

    username = session['username']
    if username == salle['owner'] or utilisateurs.get(username, {}).get('is_admin', False):
        participant = salle['participants'].get(target)
        if participant:
            participant['muted'] = not participant.get('muted', False)
            flash(f"{target} a été {'rendu muet' if participant['muted'] else 'réactivé'}.", 'info')
        else:
            flash("L'utilisateur n'est pas un participant de ce salon.", 'warning')
    else:
        flash("Vous n'avez pas les permissions pour cette action.", 'danger')

    return redirect(url_for('chat_salon', room_id=room_id))

if __name__ == '__main__':
    app.run(debug=True)
