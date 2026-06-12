const { Router } = require('express');
const { createPost, deletePost, listPosts, updatePost } = require('../controllers/postController');
const { createPostValidator, postIdParamValidator, updatePostValidator } = require('../validators/postValidators');
const { validateRequest } = require('../middleware/validateRequest');
const { authenticate } = require('../middleware/authenticate');

const router = Router();

// GET /posts - public
router.get('/', listPosts);

// POST /posts - protected
router.post('/', authenticate, createPostValidator, validateRequest, createPost);

// PUT /posts/:id - protected, owner only
router.put('/:id', authenticate, updatePostValidator, validateRequest, updatePost);

// DELETE /posts/:id - protected, owner only
router.delete('/:id', authenticate, postIdParamValidator, validateRequest, deletePost);

module.exports = router;
