const express = require('express');
const { PrismaClient } = require('@prisma/client');
const { authenticateToken } = require('../middleware/auth');
const { checkBookingConstraints } = require('../middleware/dynamicConstraints');

const router = express.Router();
const prisma = new PrismaClient();

// GET /bookings – retourne les réservations
// Les employés voient leurs réservations, les admins voient toutes les réservations
router.get('/', authenticateToken, async (req, res) => {
  try {
    const bookings = await prisma.booking.findMany({
      where: req.user.role === 'admin' ? {} : { userId: req.user.userId },
      include: { room: true, user: true }
    });
    res.json(bookings);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/', authenticateToken, checkBookingConstraints, async (req, res) => { // POST /bookings – créer une réservation avec vérifications
  try {
    const { roomId, start, end } = req.body;
    const newBooking = await prisma.booking.create({
      data: {
        roomId: parseInt(roomId),
        start: new Date(start),
        end: new Date(end),
        userId: req.user.userId,
      }
    });
    res.status(201).json(newBooking);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

module.exports = router;