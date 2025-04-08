const jwt = require('jsonwebtoken');

function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) return res.status(401).json({ error: 'Token manquant' });

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Token invalide' });
    req.user = user;
    next();
  });
}

function authorizeRole(role) { // Middleware pour vérifier le rôle (exemple : admin)
  return (req, res, next) => {
    if (req.user.role !== role) {
      return res.status(403).json({ error: "Accès refusé" });
    }
    next();
  };
}

module.exports = { authenticateToken, authorizeRole };