# B3B Events API

## Prisma

### Installation

```bash
npm install --save-dev prisma
npm install @prisma/client
npx prisma init --datasource-provider postgresql
```

### Configuration

```bash
cp .env.dist .env
```

Puis configurer l'adresse de la bdd dans ce fichier .env

### Migrations

Décrire les modèles voulus dans `prisma/schema.prisma`.

Générer et éxécuter les migrations :

```bash
npx prisma migrate dev --name <migration_name>
npx prisma generate
```
