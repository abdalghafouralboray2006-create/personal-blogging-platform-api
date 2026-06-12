const { Prisma } = require('@prisma/client');
const { AppError } = require('../utils/AppError');
const { errorResponse } = require('../utils/response');
const { isProduction } = require('../config/env');

/**
 * Translates known Prisma errors into AppError instances with
 * appropriate HTTP status codes.
 * @param {import('@prisma/client').Prisma.PrismaClientKnownRequestError} err
 */
function normalizePrismaError(err) {
  switch (err.code) {
    case 'P2002': // Unique constraint violation
      return new AppError('A record with this value already exists', 400);
    case 'P2025': // Record not found
      return new AppError('Resource not found', 404);
    default:
      return new AppError('Database error', 500);
  }
}

/**
 * Centralized error handling middleware. Must be registered last,
 * after all routes. Converts any thrown/forwarded error into the
 * standard { success, message, errors? } response shape.
 */
function errorHandler(err, _req, res, _next) {
  let appError;

  if (err instanceof AppError) {
    appError = err;
  } else if (err instanceof Prisma.PrismaClientKnownRequestError) {
    appError = normalizePrismaError(err);
  } else if (err instanceof Error) {
    appError = new AppError(isProduction ? 'Internal server error' : err.message, 500);
  } else {
    appError = new AppError('Internal server error', 500);
  }

  if (!isProduction && appError.statusCode === 500) {
    console.error(err);
  }

  res.status(appError.statusCode).json(errorResponse(appError.message, appError.errors));
}

module.exports = { errorHandler };
