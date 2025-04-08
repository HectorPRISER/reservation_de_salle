const express = require('express');
const { PrismaClient } = require('@prisma/client');
const { authenticateToken, authorizeRole } = require('../middleware/auth');

const router = express.Router();
const prisma = new PrismaClient();

// GET /rooms – liste toutes les salles
router.get('/', async (req, res) => {
  try {
    const rooms = await prisma.room.findMany();
    res.json(rooms);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// POST /rooms – création d’une salle (admin uniquement)
router.post('/', authenticateToken, authorizeRole('admin'), async (req, res) => {
  try {
    const { name, capacity, features, rules } = req.body;
    const newRoom = await prisma.room.create({
      data: {
        name,
        capacity,
        features,
        rules,
      },
    });
    res.status(201).json(newRoom);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// GET /rooms/:id – détails d’une salle
router.get('/:id', async (req, res) => {
  try {
    const room = await prisma.room.findUnique({
      where: { id: parseInt(req.params.id) },
    });
    if (!room) {
      return res.status(404).json({ error: "Salle non trouvée" });
    }
    res.json(room);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;