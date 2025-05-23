from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = 'remplacez_par_votre_cle_secrete'  # modifiez cette clé pour la production

# URL de base de l'API Node.js
API_BASE_URL = 'http://localhost:3000'


@app.route('/', methods=['GET', 'POST'])
def login():
    print("Tentative de connexion")
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
    # Vérifier que l'utilisateur est connecté (token en session)
    token = session.get('token')
    if not token:
        flash("Veuillez vous connecter", "warning")
        return redirect(url_for('login'))
        
    headers = {'Authorization': f'Bearer {token}'}
    
    # Récupérer la liste des salles depuis l'API
    try:
        res = requests.get(f"{API_BASE_URL}/rooms", headers=headers)
        if res.status_code == 200:
            rooms = res.json()
        else:
            rooms = []
    except Exception as e:
        rooms = []
    
    # Déterminer l'ID de la salle à afficher :
    # Si un ID de salle est passé en query parameter, on l'utilise, sinon on prend la première salle disponible (si existe)
    room_id = request.args.get('room_id', type=int)
    if room_id is None and rooms:
        room_id = rooms[0]['id']
    
    return render_template('calendar.html', rooms=rooms, room_id=room_id)

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
        # Supposons que la valeur est au format ISO en UTC
        utc_dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        # Convertir en fuseau local (ici, par exemple, Europe/Paris)
        local_tz = pytz.timezone('Europe/Paris')
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt.strftime(format)
    except Exception:
        return value
        
    
@app.route('/book', methods=['GET', 'POST'])
def book_room():
    token = session.get('token')
    infos = {}

    # Make sure the token exists before using it to set headers
    if not token:
        flash("Veuillez vous connecter", "warning")
        return redirect(url_for('login'))

    headers = {'Authorization': f'Bearer {token}'}
    
    # Now, you can safely make the GET request with headers
    r = requests.get(f"{API_BASE_URL}/rooms", headers=headers)
    if r.status_code == 200:
        infos['rooms'] = r.json()
    else:
        infos['rooms'] = []

    if request.method == 'POST':
        # Récupérer les données du formulaire de réservation
        room_id = request.form.get('roomId')  # Assurez-vous que ce champ correspond à votre formulaire HTML.
        start = request.form.get('start')
        end = request.form.get('end')

        # Vérifier que toutes les informations sont présentes
        if not (room_id and start and end):
            flash("Tous les champs sont obligatoires.", "danger")
            return redirect(url_for('book_room'))

        try:
            # Construire les données selon le format attendu par l'API
            booking_data = {
                "roomId": int(room_id),
                "start": start,
                "end": end
            }
        except ValueError:
            flash("Identifiant de salle non valide.", "danger")
            return redirect(url_for('book_room'))

        try:
            # Envoyer la requête POST de réservation à l'API
            response = requests.post(f"{API_BASE_URL}/bookings", json=booking_data, headers=headers)
            if response.status_code == 201:
                flash("Réservation créée avec succès", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Erreur lors de la création de la réservation", "danger")
        except Exception as e:
            flash("Erreur de connexion à l'API", "danger")
    
    # Pour GET, afficher la page de réservation
    return render_template('book.html', username=session.get('username'), rooms=infos['rooms'])
@app.route('/create_room', methods=['GET', 'POST'])
def create_room():
    token = session.get('token')
    if not token:
        flash("Veuillez vous connecter", "warning")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        name = request.form.get('name')
        capacity = request.form.get('capacity')
        features = request.form.get('features')
        
        # Transformation du champ features en liste (séparateur virgule)
        features_list = [feature.strip() for feature in features.split(',')] if features else []
        
        # Récupérer les valeurs spécifiques aux règles
        try:
            max_duration = int(request.form.get('maxDurationMinutes'))
        except (TypeError, ValueError):
            max_duration = 120  # Valeur par défaut si nécessaire
        
        try:
            min_advance = int(request.form.get('minAdvanceHours'))
        except (TypeError, ValueError):
            min_advance = 3  # Valeur par défaut si nécessaire
        
        # La case checkbox renvoie 'on' si cochée, sinon None
        allow_weekends = True if request.form.get('allowWeekends') == 'on' else False
        
        # Construire l'objet rules
        rules_obj = {
            "maxDurationMinutes": max_duration,
            "minAdvanceHours": min_advance,
            "allowWeekends": allow_weekends
        }
        
        # Préparer les données dans le format attendu par l'API
        room_data = {
            "name": name,
            "capacity": int(capacity),
            "features": features_list,
            "rules": rules_obj
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        try:
            # Envoyer la requête POST de création à l'API
            response = requests.post(f"{API_BASE_URL}/rooms", json=room_data, headers=headers)
            if response.status_code == 201:
                flash("Salle créée avec succès", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Erreur lors de la création de la salle", "danger")
        except Exception as e:
            flash("Erreur de connexion à l'API", "danger")
    
    return render_template('create_room.html', username=session.get('username'))


if __name__ == '__main__':
    app.run(debug=True)