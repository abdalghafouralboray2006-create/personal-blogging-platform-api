const { catchAsync } = require('../utils/catchAsync');
const { successResponse } = require('../utils/response');
const { AppError } = require('../utils/AppError');
const postService = require('../services/postService');

/**
 * GET /posts
 * Public endpoint returning all posts, most recent first.
 */
const listPosts = catchAsync(async (_req, res) => {
  const posts = await postService.getAllPosts();
  res.status(200).json(successResponse(posts));
});

/**
 * POST /posts
 * Protected endpoint. Creates a new post owned by the authenticated user.
 */
const createPost = catchAsync(async (req, res) => {
  if (!req.user) {
    throw new AppError('Authentication required', 401);
  }

  const { title, content } = req.body;

  const post = await postService.createPost({
    title,
    content,
    authorId: req.user.userId,
  });

  res.status(201).json(successResponse(post, 'Post created successfully'));
});

/**
 * PUT /posts/:id
 * Protected endpoint. Updates a post if the authenticated user is its owner.
 */
const updatePost = catchAsync(async (req, res) => {
  if (!req.user) {
    throw new AppError('Authentication required', 401);
  }

  const { id } = req.params;
  const { title, content } = req.body;

  const post = await postService.updatePost(id, req.user.userId, { title, content });

  res.status(200).json(successResponse(post, 'Post updated successfully'));
});

/**
 * DELETE /posts/:id
 * Protected endpoint. Deletes a post if the authenticated user is its owner.
 */
const deletePost = catchAsync(async (req, res) => {
  if (!req.user) {
    throw new AppError('Authentication required', 401);
  }

  const { id } = req.params;

  await postService.deletePost(id, req.user.userId);

  res.status(200).json(successResponse(null, 'Post deleted successfully'));
});

module.exports = { listPosts, createPost, updatePost, deletePost };
