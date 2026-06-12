const { validationResult } = require('express-validator');
const { AppError } = require('../utils/AppError');

/**
 * Runs after express-validator checks. If any validation errors were
 * recorded on the request, responds with 400 and a list of field errors.
 */
function validateRequest(req, _res, next) {
  const errors = validationResult(req);

  if (!errors.isEmpty()) {
    const formattedErrors = errors.array().map((error) => ({
      field: error.path || 'unknown',
      message: error.msg,
    }));

    return next(new AppError('Validation failed', 400, formattedErrors));
  }

  next();
}

module.exports = { validateRequest };
