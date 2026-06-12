const { catchAsync } = require('../utils/catchAsync');
const { successResponse } = require('../utils/response');
const { registerUser, loginUser } = require('../services/authService');

/**
 * POST /auth/register
 * Creates a new user account and returns the user profile with a JWT.
 */
const register = catchAsync(async (req, res) => {
  const { name, email, password } = req.body;

  const result = await registerUser({ name, email, password });

  res.status(201).json(successResponse(result, 'User registered successfully'));
});

/**
 * POST /auth/login
 * Authenticates a user and returns a JWT access token.
 */
const login = catchAsync(async (req, res) => {
  const { email, password } = req.body;

  const result = await loginUser({ email, password });

  res.status(200).json(successResponse(result, 'Login successful'));
});

module.exports = { register, login };
