const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function resetData() {
  try {
    // Supprimer toutes les réservations (Bookings) en premier, car elles dépendent des salles
    const deletedBookings = await prisma.booking.deleteMany();
    console.log(`Réservations supprimées : ${deletedBookings.count}`);

    // Supprimer toutes les salles (Rooms)
    const deletedRooms = await prisma.room.deleteMany();
    console.log(`Salles supprimées : ${deletedRooms.count}`);
  } catch (error) {
    console.error("Erreur lors du reset des données :", error);
  } finally {
    await prisma.$disconnect();
  }
}

resetData();