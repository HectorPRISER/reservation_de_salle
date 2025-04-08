const express = require('express');

const prisma = require('../utils/db.js');
const { validateEventInputsMiddleware } = require('../utils/middlewares.js')


const router = express.Router();


// Create event endpoint
router.post('/', validateEventInputsMiddleware, async (req, res, next) => {
  const { title, description, date } = req.body;

  try {
    const event = await prisma.event.create({
      data: {
        title: title,
        description,
        date: new Date(date),
      },
    });

    return res.status(201).json(event);
  } catch (error) {
    next(error);
  }
});

// List all events
router.get('/', async (req, res, next) => {
  try {
    const events = await prisma.event.findMany();
    return res.status(200).json(events);
  } catch (error) {
    next(error);
  }
});

// Get one event details
router.get('/:id', async (req, res, next) => {
  const { id } = req.params;

  try {
    const event = await prisma.event.findUnique({
      where: {
        id: parseInt(id),
      }
    });

    return res.status(200).json(event);
  } catch (error) {
    next(error);
  }
});

// Update one event
router.put('/:id', async (req, res, next) => {
  const { id } = req.params;
  const { title, description, date } = req.body;

  try {
    const event = await prisma.event.update({
      where: {
        id: parseInt(id),
      },
      data: {
        title: title,
        description: description,
        date: new Date(date),
      },
    });

    return res.status(200).json(event);
  } catch (error) {
    next(error);
  }
});

// Delete one event
router.delete('/:id', async (req, res, next) => {
  const { id } = req.params;

  try {
    const event = await prisma.event.delete({
      where: {
        id: parseInt(id),
      },
    });

    return res.status(200).json({});
  } catch (error) {
    next(error);
  }
});

module.exports = router;
