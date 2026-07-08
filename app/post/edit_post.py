# app/post/edit_post.py

from beanie import PydanticObjectId
from app.model.account import Post
from app.log.log import log_now


class EditPost:
    def __init__(self, post_id):
        """
        must match account_id with post's account_id
        """
        self.post_id = post_id

    async def _get_owned_post(self):
        """Fetch the post and verify it belongs to self.account_id. Returns (post, error_dict)."""
        post = await Post.get(PydanticObjectId(self.post_id))

        if post is None:
            return None, {
                "data": {"error": "post not found"},
                "status": False,
                "from": "EditPost",
            }

        return post, None

    async def increment_views(self):
        try:
            post, error = await self._get_owned_post()
            if error:
                return error

            post.post_views += 1
            await post.save()

            return {
                "data": {"post_views": post.post_views},
                "status": True,
                "from": "EditPost.increment_views",
            }

        except Exception as error:
            log = {
                "data": {"error": str(error)},
                "status": False,
                "from": "EditPost.increment_views",
            }
            await log_now(log)
            return log

    async def toggle_private(self, account_id):
        try:
            post, error = await self._get_owned_post()
            if error:
                return error

            if post.account_id == account_id:
                post.post_private = not post.post_private
                await post.save()

                return {
                    "data": {"post_private": post.post_private},
                    "status": True,
                    "from": "EditPost.toggle_private",
                }

            else:
                return {
                    "data": {"error": "not authorized to modify this post"},
                    "status": False,
                    "from": "EditPost.toggle_private",
                }

        except Exception as error:
            log = {
                "data": {"error": str(error)},
                "status": False,
                "from": "EditPost.toggle_private",
            }
            await log_now(log)
            return log
