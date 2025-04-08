#!/bin/sh
set -e

echo "Waiting for database connection on db:5432..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is up!"

echo "Generating Prisma client..."
npx prisma generate --schema=./prisma/schema.prisma

echo "Running Prisma migrations..."
npx prisma migrate deploy --schema=./prisma/schema.prisma

echo "Seeding the database..."
node prisma/seed.js

echo "Starting the application..."
exec npm run dev