# app/post/one_post.py

from beanie import PydanticObjectId
from app.model.account import Post
from app.log.log import log_now


class OnePost:

    async def get_one_post(self, post_id, viewer_account_id=None):
        try:

            post = await Post.get(PydanticObjectId(post_id))

            if post is None:
                return {
                    "data": {"error": "post not found"},
                    "status": False,
                    "from": "OnePost.get_one_post",
                }

            if post.post_private and post.account_id != viewer_account_id:
                return {
                    "data": {"error": "post is private"},
                    "status": False,
                    "from": "OnePost.get_one_post",
                }

            if post.post_blocked:
                return {
                    "data": {"error": "post not found"},
                    "status": False,
                    "from": "OnePost.get_one_post",
                }

            return {
                "data": {"post": post.model_dump(mode="json")},
                "status": True,
                "from": "OnePost.get_one_post",
            }

        except Exception as error:

            log = {
                "data": {"error": str(error)},
                "status": False,
                "from": "OnePost.get_one_post",
            }

            await log_now(log)

            return log

