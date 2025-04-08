# Reservation de Salle API

Ce projet est une API de gestion des réservations de salles, conteneurisée avec PostgreSQL, Adminer et Node.js.

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

## Accès

- **API** : [http://localhost:3000](http://localhost:3000)
- **Adminer** : [http://localhost:8081](http://localhost:8081)

Profitez de votre application !
