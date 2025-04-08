// prisma/seed.js
const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcrypt');

const prisma = new PrismaClient();

async function main() {
  const passwordAdmin = await bcrypt.hash("admin", 10);
  const passwordEmployee = await bcrypt.hash("employee", 10);

  // Créer ou mettre à jour l'utilisateur admin
  await prisma.user.upsert({
    where: { username: "admin" },
    update: {
      password: passwordAdmin,
      role: "admin"
    },
    create: {
      username: "admin",
      password: passwordAdmin,
      role: "admin"
    }
  });

  // Créer ou mettre à jour l'utilisateur employee
  await prisma.user.upsert({
    where: { username: "employee" },
    update: {
      password: passwordEmployee,
      role: "employee"
    },
    create: {
      username: "employee",
      password: passwordEmployee,
      role: "employee"
    }
  });

  console.log("Utilisateurs admin et employee créés ou mis à jour.");
}

main()
  .catch(e => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
