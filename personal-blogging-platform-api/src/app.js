const express = require('express');
const cors = require('cors');
const authRoutes = require('./routes/authRoutes');
const postRoutes = require('./routes/postRoutes');
const { notFoundHandler } = require('./middleware/notFoundHandler');
const { errorHandler } = require('./middleware/errorHandler');
const { successResponse } = require('./utils/response');

/**
 * Builds and returns a configured Express application instance.
 */
function createApp() {
  const app = express();

  // Core middleware
  app.use(cors());
  app.use(express.json());

  // Health check
  app.get('/', (_req, res) => {
    res.status(200).json(successResponse({ status: 'ok' }, 'Personal Blogging Platform API is running'));
  });

  // Routes
  app.use('/auth', authRoutes);
  app.use('/posts', postRoutes);

  // 404 + centralized error handling (must be registered last)
  app.use(notFoundHandler);
  app.use(errorHandler);

  return app;
}

module.exports = { createApp };
