# Reservation de Salle API

Ce projet est une API de gestion des réservations de salles, conteneurisée avec PostgreSQL, Adminer et Node.js.
Une ébauche de front end et disponible.

## Installation

### 1. Créer le fichier `.env`

À la racine du projet, créez un fichier `.env` avec le contenu suivant (vous pouvez adapter les valeurs si nécessaire) :

```env
DATABASE_URL=postgres://postgres:postgres@db:5432/app?schema=public
JWT_SECRET=your-secret-key-here
PORT=3000
```

### 2. Lancer les conteneurs

Construisez et démarrez tous les services (API, base de données et Adminer) avec Docker Compose :

```bash
docker-compose up --build
```
⚠️ Si une erreur est causée à cause de entrypoint.sh, recréez simplement le fichier pour l'encoder en fonction de votre OS.

### Accès:
	-	API : http://127.0.0.1:3000
	-	Adminer : http://127.0.0.1:8081


### TESTS:
Les tests automatisées permettent de s'assurer du bon fonctionnement de tous les composants du backend, mais également de créer quelques données.
```bash
python tests/tester.py
```

### FRONT END:

Pour lancer le serveur front:
Requirements: Python v >= 3.12

```bash
cd front_dev
pip install requirements.txt
python app.py
```

Login admin: 
username: admin	
password: admin
