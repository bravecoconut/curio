# app/post/all_posts.py

from app.model.account import Post
from app.log.log import log_now


class AllPosts:
    def __init__(self, account_id):
        self.account_id = account_id

    async def get_all_posts(self, start=1, end=10):
        """
        Fetch posts by a 1-indexed inclusive range, e.g. start=1, end=10
        gets the first 10 posts; start=11, end=20 gets the next 10.
        """
        try:
            if start < 1 or end < start:
                return {
                    "data": {
                        "error": "invalid range: start must be >= 1 and end >= start"
                    },
                    "status": False,
                    "from": "AllPosts.get_all_posts",
                }

            skip = start - 1
            limit = end - start + 1


            posts = (
                await Post.find(Post.account_id == self.account_id)
                .sort(-Post.date_created)
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
                "from": "AllPosts.get_all_posts",
            }

        except Exception as error:
            log = {
                "data": {"error": str(error)},
                "status": False,
                "from": "AllPosts.get_all_posts",
            }
            await log_now(log)
            return log
