/**
 * Builds a standard success response body.
 * @param {*} data
 * @param {string} [message]
 */
function successResponse(data, message) {
  return {
    success: true,
    ...(message ? { message } : {}),
    data,
  };
}

/**
 * Builds a standard error response body.
 * @param {string} message
 * @param {Array<{field: string, message: string}>} [errors]
 */
function errorResponse(message, errors) {
  return {
    success: false,
    message,
    ...(errors ? { errors } : {}),
  };
}

module.exports = { successResponse, errorResponse };
