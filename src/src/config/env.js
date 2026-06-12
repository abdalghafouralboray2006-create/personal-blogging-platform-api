const { config: loadEnv } = require('dotenv');

loadEnv();

/**
 * Reads a required environment variable.
 * Throws at startup if it is missing, so misconfiguration fails fast.
 */
function requireEnv(name) {
  const value = process.env[name];
  if (!value || value.trim().length === 0) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

const env = {
  databaseUrl: requireEnv('DATABASE_URL'),
  jwtSecret: requireEnv('JWT_SECRET'),
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '1h',
  port: Number(process.env.PORT || 3000),
  nodeEnv: process.env.NODE_ENV || 'development',
};

const isProduction = env.nodeEnv === 'production';

module.exports = { env, isProduction };
