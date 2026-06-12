const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { prisma } = require('../database/prismaClient');
const { env } = require('../config/env');
const { AppError } = require('../utils/AppError');

const SALT_ROUNDS = 10;

/**
 * Converts a Prisma User record into the public-facing shape
 * (omits the password hash).
 * @param {{id: string, name: string, email: string, createdAt: Date}} user
 */
function toPublicUser(user) {
  return {
    id: user.id,
    name: user.name,
    email: user.email,
    createdAt: user.createdAt,
  };
}

/**
 * Signs a JWT access token containing the user's id and email.
 * @param {{userId: string, email: string}} payload
 */
function generateToken(payload) {
  return jwt.sign(payload, env.jwtSecret, { expiresIn: env.jwtExpiresIn });
}

/**
 * Registers a new user: hashes the password, ensures email uniqueness,
 * persists the user, and returns the public profile with a JWT token.
 * @param {{name: string, email: string, password: string}} input
 */
async function registerUser(input) {
  const normalizedEmail = input.email.trim().toLowerCase();

  const existingUser = await prisma.user.findUnique({
    where: { email: normalizedEmail },
  });

  if (existingUser) {
    throw new AppError('Email is already registered', 400);
  }

  const passwordHash = await bcrypt.hash(input.password, SALT_ROUNDS);

  const user = await prisma.user.create({
    data: {
      name: input.name.trim(),
      email: normalizedEmail,
      passwordHash,
    },
  });

  const token = generateToken({ userId: user.id, email: user.email });

  return { user: toPublicUser(user), token };
}

/**
 * Authenticates a user by verifying their email and password,
 * returning a JWT token on success.
 * @param {{email: string, password: string}} input
 */
async function loginUser(input) {
  const normalizedEmail = input.email.trim().toLowerCase();

  const user = await prisma.user.findUnique({
    where: { email: normalizedEmail },
  });

  if (!user) {
    throw new AppError('Invalid email or password', 401);
  }

  const isPasswordValid = await bcrypt.compare(input.password, user.passwordHash);

  if (!isPasswordValid) {
    throw new AppError('Invalid email or password', 401);
  }

  const token = generateToken({ userId: user.id, email: user.email });

  return { user: toPublicUser(user), token };
}

module.exports = { registerUser, loginUser };
