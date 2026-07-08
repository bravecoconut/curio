# app/post/explore_posts.py

from app.model.account import Post
from app.log.log import log_now


class ExplorePosts:
    async def get_explore_posts(self, start=1, end=10, sort_by="date_created"):
        """
        Fetch public posts across all users, 1-indexed inclusive range.
        sort_by: "date_created" (newest first) or "post_views" / "post_likes" (most popular first)
        """
        try:
            if start < 1 or end < start:
                return {
                    "data": {
                        "error": "invalid range: start must be >= 1 and end >= start"
                    },
                    "status": False,
                    "from": "ExplorePosts.get_explore_posts",
                }

            skip = start - 1
            limit = end - start + 1


            sort_field_map = {
                "date_created": -Post.date_created,
                "post_views": -Post.post_views,
                "post_likes": -Post.post_shares,
            }

            sort_field = sort_field_map.get(sort_by, -Post.date_created)

            posts = (
                await Post.find(
                    Post.post_private == False,
                    Post.post_blocked == False,
                )
                .sort(sort_field)
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
                "from": "ExplorePosts.get_explore_posts",
            }

        except Exception as error:
            log = {
                "data": {"error": str(error)},
                "status": False,
                "from": "ExplorePosts.get_explore_posts",
            }
            await log_now(log)
            return log
