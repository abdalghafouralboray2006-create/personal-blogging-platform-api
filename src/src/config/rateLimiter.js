const rateLimit = require('express-rate-limit');

/**
 * Restricts login attempts to mitigate brute-force attacks.
 * Limit: 5 requests per 15 minutes per IP address.
 */
const loginRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    success: false,
    message: 'Too many login attempts. Please try again after 15 minutes.',
  },
});

module.exports = { loginRateLimiter };
