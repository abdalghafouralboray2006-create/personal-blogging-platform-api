/**
 * Represents an operational error with an associated HTTP status code.
 * Thrown intentionally by controllers/services and caught by the
 * centralized error handler.
 */
class AppError extends Error {
  /**
   * @param {string} message
   * @param {number} statusCode
   * @param {Array<{field: string, message: string}>} [errors]
   */
  constructor(message, statusCode, errors) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
    this.errors = errors;
  }
}

module.exports = { AppError };
