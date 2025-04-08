const { z } = require('zod');

const userLoginSchema = z.object({
  username: z.string().min(1, "Username requis"),
  password: z.string().min(1, "Mot de passe requis"),
});

module.exports = { userLoginSchema };