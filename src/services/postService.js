const { prisma } = require('../database/prismaClient');
const { AppError } = require('../utils/AppError');

const postWithAuthorSelect = {
  id: true,
  title: true,
  content: true,
  authorId: true,
  createdAt: true,
  updatedAt: true,
  author: {
    select: {
      id: true,
      name: true,
    },
  },
};

/**
 * Returns all posts, most recent first, including a minimal author summary.
 * This endpoint is public and requires no authentication.
 */
async function getAllPosts() {
  return prisma.post.findMany({
    orderBy: { createdAt: 'desc' },
    select: postWithAuthorSelect,
  });
}

/**
 * Fetches a single post by id, including author summary.
 * Throws 404 if the post does not exist.
 * @param {string} postId
 */
async function findPostOrFail(postId) {
  const post = await prisma.post.findUnique({
    where: { id: postId },
    select: postWithAuthorSelect,
  });

  if (!post) {
    throw new AppError('Post not found', 404);
  }

  return post;
}

/**
 * Creates a new post owned by the given author.
 * @param {{title: string, content: string, authorId: string}} input
 */
async function createPost(input) {
  return prisma.post.create({
    data: {
      title: input.title.trim(),
      content: input.content.trim(),
      authorId: input.authorId,
    },
    select: postWithAuthorSelect,
  });
}

/**
 * Updates an existing post after verifying it exists and that the
 * requesting user is its owner.
 * @param {string} postId
 * @param {string} requestingUserId
 * @param {{title?: string, content?: string}} input
 */
async function updatePost(postId, requestingUserId, input) {
  const post = await findPostOrFail(postId);

  if (post.authorId !== requestingUserId) {
    throw new AppError('You do not have permission to modify this post', 403);
  }

  return prisma.post.update({
    where: { id: postId },
    data: {
      ...(input.title !== undefined ? { title: input.title.trim() } : {}),
      ...(input.content !== undefined ? { content: input.content.trim() } : {}),
    },
    select: postWithAuthorSelect,
  });
}

/**
 * Deletes an existing post after verifying it exists and that the
 * requesting user is its owner.
 * @param {string} postId
 * @param {string} requestingUserId
 */
async function deletePost(postId, requestingUserId) {
  const post = await findPostOrFail(postId);

  if (post.authorId !== requestingUserId) {
    throw new AppError('You do not have permission to delete this post', 403);
  }

  await prisma.post.delete({ where: { id: postId } });
}

module.exports = { getAllPosts, createPost, updatePost, deletePost };
