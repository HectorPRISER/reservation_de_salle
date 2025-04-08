const express = require('express');
const app = express();
const cors = require('cors');
const authRoutes = require('./routes/auth');
const roomRoutes = require('./routes/rooms');
const bookingRoutes = require('./routes/bookings');

app.use(express.json());
app.use(cors());


app.use('/auth', authRoutes);

app.use('/rooms', roomRoutes); // SALLES

app.use('/bookings', bookingRoutes); // RESERVATIONS

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});