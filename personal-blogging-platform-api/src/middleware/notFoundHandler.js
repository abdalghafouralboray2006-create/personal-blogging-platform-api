const { errorResponse } = require('../utils/response');

/**
 * Handles requests to routes that do not exist.
 * Registered after all valid routes, before the error handler.
 */
function notFoundHandler(req, res) {
  res.status(404).json(errorResponse(`Route ${req.method} ${req.originalUrl} not found`));
}

module.exports = { notFoundHandler };
