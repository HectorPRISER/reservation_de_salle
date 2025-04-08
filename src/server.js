const express = require('express');
const { rateLimit } = require('express-rate-limit');
const helmet = require('helmet');
const { z } = require('zod');

const eventsController = require('./controllers/eventsController.js');
const profilesController = require('./controllers/profilesController.js');
const usersController = require('./controllers/usersController.js');
const { authMiddleware, customLogMiddleware } = require('./utils/middlewares.js');

const port = 3000;

if (!process.env.JWT_SECRET) {
  throw new Error('Please set JWT_SECRET variable.')
}

const app = express();

const limiter = rateLimit({
	windowMs: 1 * 60 * 1000, // 1 minute
	limit: 10, // Limit each IP to 100 requests per `window`
	standardHeaders: 'draft-8', // draft-6: `RateLimit-*` headers; draft-7 & draft-8: combined `RateLimit` header
	legacyHeaders: false, // Disable the `X-RateLimit-*` headers.
})

// Global middlewares
app.use(limiter);
app.use(customLogMiddleware);
app.use(helmet());
app.use(express.json()) // for parsing application/json


// Endpoints
app.use('/events', authMiddleware, eventsController);
app.use('/profiles', profilesController);
app.use('/users', usersController);


// Misc
app.use((err, req, res, next) => {
  if (res.statusCode === 401) {
    return res.json({ message: 'Forbidden' });
  }

  if (err instanceof z.ZodError) {
    const errors = err.errors.map(item => ({
      input: item.path[0],
      message: item.message,
    }));

    return res.status(400).json({errors});
  }

  return res.status(500).send('Something broke very hard!');
});

app.listen(port, () => {
  console.log(`App listening on port ${port}`);
})
