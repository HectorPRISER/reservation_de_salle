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

// GET /rooms/:id/availability?date=YYYY-MM-DD – retourne les créneaux disponibles pour une journée
router.get('/:id/availability', async (req, res) => {
  try {
    const roomId = parseInt(req.params.id);
    if (isNaN(roomId)) {
      return res.status(400).json({ error: "ID de salle invalide" });
    }
    
    // Récupère la date transmise en query string
    const dateParam = req.query.date;
    if (!dateParam) {
      return res.status(400).json({ error: "Date manquante dans la requête (format YYYY-MM-DD)" });
    }
    
    const queryDate = new Date(dateParam);
    if (isNaN(queryDate.getTime())) {
      return res.status(400).json({ error: "Date invalide" });
    }
    
    // Définir les bornes de la journée (ici, de 08h à 18h)
    const dayStart = new Date(queryDate);
    dayStart.setHours(8, 0, 0, 0);
    const dayEnd = new Date(queryDate);
    dayEnd.setHours(18, 0, 0, 0);
    
    // Récupérer toutes les réservations pour la salle sur cette journée (ordre croissant par heure de début)
    const bookings = await prisma.booking.findMany({
      where: {
        roomId: roomId,
        start: {
          gte: dayStart
        },
        end: {
          lte: dayEnd
        }
      },
      orderBy: { start: 'asc' }
    });
    
    // Calculer les créneaux disponibles en considérant que la journée de travail est de 08h à 18h.
    const availableSlots = [];
    let currentStart = dayStart;
    
    // Si aucune réservation, toute la journée est libre
    if (bookings.length === 0) {
      availableSlots.push({ start: currentStart, end: dayEnd });
    } else {
      bookings.forEach(booking => {
        const bookingStart = new Date(booking.start);
        const bookingEnd = new Date(booking.end);
        // Si un intervalle est libre avant la réservation actuelle
        if (currentStart < bookingStart) {
          availableSlots.push({ start: new Date(currentStart), end: new Date(bookingStart) });
        }
        // Mettre à jour currentStart à la fin de la réservation en cours
        currentStart = bookingEnd;
      });
      // Vérifier s'il reste un créneau libre après la dernière réservation
      if (currentStart < dayEnd) {
        availableSlots.push({ start: currentStart, end: dayEnd });
      }
    }
    
    // Formatage des dates en ISO pour la réponse
    const formattedSlots = availableSlots.map(slot => ({
      start: slot.start.toISOString(),
      end: slot.end.toISOString()
    }));
    
    res.json({ availability: formattedSlots });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;