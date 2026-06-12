const { PrismaClient } = require('@prisma/client');
const { isProduction } = require('../config/env');

/**
 * Prisma client singleton.
 *
 * In serverless environments (Vercel) modules can be re-evaluated across
 * invocations, so we cache the client on the global object in development
 * to avoid exhausting database connections during hot-reloads.
 */
const prisma =
  global.prismaClient ||
  new PrismaClient({
    log: isProduction ? ['error'] : ['warn', 'error'],
  });

if (!isProduction) {
  global.prismaClient = prisma;
}

module.exports = { prisma };
