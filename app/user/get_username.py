# app/user/get_username.py

from app.model.account import User, Post
from app.log.log import log_now


class GetUsername:
    def __init__(self, username):
        self.username = username

    async def get_username_all_info(self):
        try:
            user = await User.find_one(User.username == self.username)

            if user is None:
                return {
                    "data": {"error": "user not found"},
                    "status": False,
                    "from": "GetUsername.get_username_all_info",
                }

            return {
                "data": {"user": user.model_dump(mode="json")},
                "status": True,
                "from": "GetUsername.get_username_all_info",
            }

        except Exception as error:
            log = {
                "data": {"error": str(error)},
                "status": False,
                "from": "GetUsername.get_username_all_info",
            }
            await log_now(log)
            return log

    async def get_username_all_posts(self, start, end, viewer_account_id=None):
        try:
            user_info = await self.get_username_all_info()

            if not user_info.get("status"):
                return user_info

            account_id = user_info["data"]["user"]["account_id"]
            is_owner = viewer_account_id == account_id

            if start < 1 or end < start:
                return {
                    "data": {"error": "invalid range: start must be >= 1 and end >= start"},
                    "status": False,
                    "from": "GetUsername.get_username_all_posts",
                }

            skip = start - 1
            limit = end - start + 1

            if is_owner:
                query = Post.find(Post.account_id == account_id)
            else:
                query = Post.find(
                    Post.account_id == account_id,
                    Post.post_private == False,
                    Post.post_blocked == False,
                )

            posts = (
                await query.sort(-Post.date_created)
                .skip(skip)
                .limit(limit)
                .to_list()
            )

            return {
                "data": {
                    "posts": [post.model_dump(mode="json") for post in posts],
                    "count": len(posts),
                    "range": {"start": start, "end": end},
                },
                "status": True,
                "from": "GetUsername.get_username_all_posts",
            }

        except Exception as error:
            log = {
                "data": {"error": str(error)},
                "status": False,
                "from": "GetUsername.get_username_all_posts",
            }
            await log_now(log)
            return log