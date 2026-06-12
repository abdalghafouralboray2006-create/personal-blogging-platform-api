const { body } = require('express-validator');

/**
 * Password requirements: minimum 8 characters, at least one number,
 * and at least one special character.
 */
const PASSWORD_MIN_LENGTH = 8;
const PASSWORD_NUMBER_REGEX = /\d/;
const PASSWORD_SPECIAL_CHAR_REGEX = /[!@#$%^&*(),.?":{}|<>_\-+=~`[\]\\/;']/;

const registerValidator = [
  body('name').trim().notEmpty().withMessage('Name is required'),

  body('email')
    .trim()
    .notEmpty()
    .withMessage('Email is required')
    .isEmail()
    .withMessage('Email must be a valid email address')
    .normalizeEmail(),

  body('password')
    .notEmpty()
    .withMessage('Password is required')
    .isLength({ min: PASSWORD_MIN_LENGTH })
    .withMessage(`Password must be at least ${PASSWORD_MIN_LENGTH} characters long`)
    .matches(PASSWORD_NUMBER_REGEX)
    .withMessage('Password must contain at least one number')
    .matches(PASSWORD_SPECIAL_CHAR_REGEX)
    .withMessage('Password must contain at least one special character'),
];

const loginValidator = [
  body('email')
    .trim()
    .notEmpty()
    .withMessage('Email is required')
    .isEmail()
    .withMessage('Email must be a valid email address')
    .normalizeEmail(),

  body('password').notEmpty().withMessage('Password is required'),
];

module.exports = { registerValidator, loginValidator };
