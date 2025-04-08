const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const { PrismaClient } = require('@prisma/client');
const { userLoginSchema } = require('../utils/validators');

const router = express.Router();
const prisma = new PrismaClient();

router.post('/login', async (req, res) => {
  try {
    const { username, password } = userLoginSchema.parse(req.body); // Validation des données avec Zod

    const user = await prisma.user.findUnique({ where: { username } });
    if (!user) {
      return res.status(401).json({ error: "Utilisateur non trouvé" });
    }
    const valid = await bcrypt.compare(password, user.password);
    if (!valid) {
      return res.status(401).json({ error: "Mot de passe invalide" });
    }
    const token = jwt.sign({ userId: user.id, role: user.role }, process.env.JWT_SECRET, { // Création du token
      expiresIn: '1h'
    });
    res.json({ token });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

router.post('/register', async (req, res) => {
  try {
    const { username, password } = userLoginSchema.parse(req.body); // Validation des données avec Zod

    const hashedPassword = await bcrypt.hash(password, 10); // Hachage du mot de passe
    const user = await prisma.user.create({
      data: {
        username,
        password: hashedPassword,
        role: 'user' // Rôle par défaut
      }
    });
    res.status(201).json({ message: "Utilisateur créé", userId: user.id });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});




module.exports = router;