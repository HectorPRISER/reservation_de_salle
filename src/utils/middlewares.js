const jwt = require('jsonwebtoken');
const { z } = require('zod');

const prisma = require('../utils/db.js');

const Event = z.object({
  title: z.string().min(3),
  description: z.string().min(10),
  date: z.string().datetime({ local: true }),
}).required();

function customLogMiddleware(req, res, next) {
  const requestDateTime = new Date();

  res.on('finish', () => {
    const requestTreatmentTime = new Date() - requestDateTime;
    console.log(`[${requestDateTime.toISOString()}] ${req.method} ${req.path} - ${requestTreatmentTime}ms`);
  });

  next();
}

function validateEventInputsMiddleware(req, res, next) {
  Event.parse(req.body);
  next();
}

async function authMiddleware(req, res, next) {
  try {
    // If no authorization header
    if (!req.headers.authorization) { throw new Error(); }

    // If token has wrong format
    const authorizationHeader = req.headers.authorization.split(' ');
    if (authorizationHeader[0] !== 'Bearer') { throw new Error(); }

    // Compare token with the last one recorded in db
    const authToken = (await prisma.authToken.findMany({
      take: 1,
      orderBy: {
        id: 'desc',
      },
    }))[0];
    if (!authToken) { throw new Error(); }

    // Extract token from authorization header
    let tokenDecoded = {};
    jwt.verify(authToken.token, process.env.JWT_SECRET, (err, decoded) => {
      if (err) { console.log(err); throw new Error(err); }
      tokenDecoded = decoded;
    });

    // Record the user id in request for future use
    const user = await prisma.user.findUnique({
      where: {
        id: authToken.userId,
      },
      include: { profiles: true }
    });
    console.log(user);
    req.user = user;
  } catch (error) {
    res.status(401);
    next(error);
  }

  next();
}

module.exports = {
  authMiddleware,
  customLogMiddleware,
  validateEventInputsMiddleware,
}