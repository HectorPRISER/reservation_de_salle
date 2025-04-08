const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function checkBookingConstraints(req, res, next) {
  try {
    const { roomId, start, end } = req.body;
    const bookingStart = new Date(start);
    const bookingEnd = new Date(end);
    const now = new Date();

    const room = await prisma.room.findUnique({ where: { id: parseInt(roomId) } }); // Récupération de la salle et de ses règles
    if (!room) {
      return res.status(404).json({ error: "Salle non trouvée" });
    }
    const rules = room.rules; // On suppose que rules est un objet JSON déjà parsé

    
    const durationMinutes = (bookingEnd - bookingStart) / (1000 * 60); // 1. Vérification de la durée maximale
    if (rules.maxDurationMinutes && durationMinutes > rules.maxDurationMinutes) {
      return res.status(400).json({ error: `La salle ${room.name} n'autorise pas les réservations de plus de ${rules.maxDurationMinutes} minutes.` });
    }

    
    const dayOfWeek = bookingStart.getDay(); // 2. Vérification de l’interdiction de réserver le week-end
    if (!rules.allowWeekends && (dayOfWeek === 0 || dayOfWeek === 6)) { // En JS, 0 = dimanche, 6 = samedi
      return res.status(400).json({ error: `La salle ${room.name} n'autorise pas les réservations le week-end.` });
    }

    const minAdvanceHours = rules.minAdvanceHours || 0; // 3. Vérification du délai minimal avant réservation
    const diffHours = (bookingStart - now) / (1000 * 60 * 60);
    if (diffHours < minAdvanceHours) {
      return res.status(400).json({ error: `La réservation doit être effectuée au moins ${minAdvanceHours} heures à l'avance.` });
    }

    const conflictingBooking = await prisma.booking.findFirst({  // 4. Vérifier le conflit de réservation (aucun chevauchement)
      where: {
        roomId: parseInt(roomId),
        // Condition : les réservations existantes empiètent sur le créneau demandé
        AND: [
          { start: { lt: bookingEnd } },
          { end: { gt: bookingStart } }
        ]
      }
    });
    if (conflictingBooking) {
      return res.status(400).json({ error: "Le créneau horaire demandé est en conflit avec une réservation existante." });
    }

    next();
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

module.exports = { checkBookingConstraints };