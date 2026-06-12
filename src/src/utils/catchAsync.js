/**
 * Wraps an async controller function so that any rejected promise
 * is forwarded to Express's error handling middleware via next().
 *
 * @param {(req: import('express').Request, res: import('express').Response, next: import('express').NextFunction) => Promise<unknown>} handler
 */
function catchAsync(handler) {
  return (req, res, next) => {
    handler(req, res, next).catch(next);
  };
}

module.exports = { catchAsync };
