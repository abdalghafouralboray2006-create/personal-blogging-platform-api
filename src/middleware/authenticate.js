const jwt = require('jsonwebtoken');
const { env } = require('../config/env');
const { AppError } = require('../utils/AppError');

/**
 * Verifies the JWT supplied in the Authorization header, then attaches
 * the decoded user information (userId, email) to req.user.
 *
 * Expects header format: "Authorization: Bearer <token>"
 */
function authenticate(req, _res, next) {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return next(new AppError('Authentication token is missing', 401));
  }

  const token = authHeader.split(' ')[1];

  if (!token) {
    return next(new AppError('Authentication token is missing', 401));
  }

  try {
    const decoded = jwt.verify(token, env.jwtSecret);
    req.user = { userId: decoded.userId, email: decoded.email };
    next();
  } catch {
    return next(new AppError('Invalid or expired token', 401));
  }
}

module.exports = { authenticate };
