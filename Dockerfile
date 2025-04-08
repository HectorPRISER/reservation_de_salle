FROM node:22.14.0

# Mettre à jour la liste des paquets et installer netcat
RUN apt-get update && apt-get install -y netcat-traditional

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de dépendances et installer les modules
COPY package*.json ./
RUN npm install
RUN npm install -g nodemon

# Copier le dossier Prisma, le code source, et le fichier .env
COPY prisma ./prisma
COPY src ./src
COPY .env ./

# Copier le script d'entrypoint et le rendre exécutable
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Démarrer l'application en utilisant l'entrypoint
ENTRYPOINT [ "/app/entrypoint.sh" ]
