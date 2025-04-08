from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'remplacez_par_votre_cle_secrete'  # modifiez cette clé pour la production

# URL de base de l'API Node.js
API_BASE_URL = 'http://localhost:3000'


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.form.get('username')
        password = request.form.get('password')
        credentials = {"username": username, "password": password}
        
        # Envoyer la requête de login à l'API
        try:
            r = requests.post(f"{API_BASE_URL}/auth/login", json=credentials)
        except Exception as e:
            flash("Erreur de connexion à l'API", "danger")
            return redirect(url_for('login'))
            
        if r.status_code == 200:
            data = r.json()
            session['token'] = data['token']
            session['username'] = username
            flash("Connexion réussie", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Échec de l'authentification, vérifiez vos identifiants", "danger")
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    # Vérifier que l'utilisateur est connecté (token stocké en session)
    token = session.get('token')
    if not token:
        flash("Veuillez vous connecter", "warning")
        return redirect(url_for('login'))
    
    headers = {'Authorization': f'Bearer {token}'}
    infos = {}
    
    # Récupérer la liste des salles
    try:
        r = requests.get(f"{API_BASE_URL}/rooms", headers=headers)
        if r.status_code == 200:
            infos['rooms'] = r.json()
        else:
            infos['rooms'] = []
    except Exception as e:
        infos['rooms'] = []
    
    # Récupérer la liste des réservations
    try:
        r = requests.get(f"{API_BASE_URL}/bookings", headers=headers)
        if r.status_code == 200:
            infos['bookings'] = r.json()
        else:
            infos['bookings'] = []
    except Exception as e:
        infos['bookings'] = []
    
    # Vous pouvez ajouter d'autres appels à l'API ici (ex. : détails d'une salle, disponibilité, etc.)
    
    return render_template('dashboard.html', infos=infos, username=session.get('username'))


@app.route('/calendar')
def calendar_view():
    # Cette route affiche un calendrier avec les créneaux disponibles pour une salle donnée.
    token = session.get('token')
    if not token:
        flash("Veuillez vous connecter", "warning")
        return redirect(url_for('login'))
        
    # Pour cet exemple, nous fixons l'ID de la salle à 1.
    # Vous pouvez adapter ultérieurement pour permettre à l'utilisateur de choisir une salle.
    room_id = 1
    return render_template('calendar.html', room_id=room_id)

@app.route('/logout')
def logout():
    session.clear()
    flash("Déconnexion réussie", "info")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.form.get('username')
        password = request.form.get('password')
        credentials = {"username": username, "password": password}
        
        # Envoyer la requête de login à l'API
        try:
            r = requests.post(f"{API_BASE_URL}/auth/register", json=credentials)
        except Exception as e:
            flash("Erreur de connexion à l'API", "danger")
            return redirect(url_for('register'))
            
        if r.status_code == 200:
            data = r.json()
            session['token'] = data['token']
            session['username'] = username
            flash("Inscription réussie", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Échec de l'inscription, vérifiez vos identifiants", "danger")
    return render_template('register.html')

@app.route('/room/<int:room_id>')
def room_details(room_id):
    # Vérifier que l'utilisateur est connecté (token stocké en session)
    token = session.get('token')
    if not token:
        flash("Veuillez vous connecter", "warning")
        return redirect(url_for('login'))
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Récupérer les détails de la salle
    try:
        r = requests.get(f"{API_BASE_URL}/rooms/{room_id}", headers=headers)
        if r.status_code == 200:
            room_details = r.json()
        else:
            room_details = {}
    except Exception as e:
        room_details = {}
    
    return render_template('room_details.html', room=room_details)


# Filtre pour formater les dates ISO en format lisible (ex: 'dd/mm/YYYY HH:MM')
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y %H:%M'):
    try:
        # Remplace "Z" pour s'assurer du bon format, puis convertir
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime(format)
    except Exception:
        return value

if __name__ == '__main__':
    app.run(debug=True)