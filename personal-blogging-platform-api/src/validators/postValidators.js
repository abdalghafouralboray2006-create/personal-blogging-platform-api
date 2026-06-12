const { body, param } = require('express-validator');

const createPostValidator = [
  body('title').trim().notEmpty().withMessage('Title is required'),
  body('content').trim().notEmpty().withMessage('Content is required'),
];

const updatePostValidator = [
  param('id').isUUID().withMessage('Post id must be a valid UUID'),

  body('title').optional().trim().notEmpty().withMessage('Title cannot be empty'),

  body('content').optional().trim().notEmpty().withMessage('Content cannot be empty'),

  body().custom((value) => {
    if (value.title === undefined && value.content === undefined) {
      throw new Error('At least one of title or content must be provided');
    }
    return true;
  }),
];

const postIdParamValidator = [param('id').isUUID().withMessage('Post id must be a valid UUID')];

module.exports = { createPostValidator, updatePostValidator, postIdParamValidator };
