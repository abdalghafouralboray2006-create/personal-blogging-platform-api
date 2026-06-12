const { Router } = require('express');
const { login, register } = require('../controllers/authController');
const { loginValidator, registerValidator } = require('../validators/authValidators');
const { validateRequest } = require('../middleware/validateRequest');
const { loginRateLimiter } = require('../config/rateLimiter');

const router = Router();

// POST /auth/register
router.post('/register', registerValidator, validateRequest, register);

// POST /auth/login (rate limited: 5 attempts per 15 minutes per IP)
router.post('/login', loginRateLimiter, loginValidator, validateRequest, login);

module.exports = router;
