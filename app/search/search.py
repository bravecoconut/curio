# app/search/search.py

from app.model.account import User, Post
from app.log.log import log_now


class Search:
    async def search_profiles(self, keyword, start=1, end=10):
        """Search usernames containing the keyword (case-insensitive, partial match)."""
        try:
            if not keyword or not keyword.strip():
                return {
                    "data": {"error": "keyword is required"},
                    "status": False,
                    "from": "Search.search_profiles",
                }

            if start < 1 or end < start:
                return {
                    "data": {"error": "invalid range: start must be >= 1 and end >= start"},
                    "status": False,
                    "from": "Search.search_profiles",
                }

            skip = start - 1
            limit = end - start + 1

            users = (
                await User.find(
                    {"username": {"$regex": keyword, "$options": "i"}}
                )
                .skip(skip)
                .limit(limit)
                .to_list()
            )

            return {
                "data": {
                    "users": [user.model_dump(mode="json") for user in users],
                    "count": len(users),
                    "range": {"start": start, "end": end},
                },
                "status": True,
                "from": "Search.search_profiles",
            }

        except Exception as error:
            log = {
                "data": {"error": str(error)},
                "status": False,
                "from": "Search.search_profiles",
            }
            await log_now(log)
            return log

    async def search_posts(self, keyword, start=1, end=10):
        """Search posts where post_fact or post_research contains the keyword."""
        try:
            if not keyword or not keyword.strip():
                return {
                    "data": {"error": "keyword is required"},
                    "status": False,
                    "from": "Search.search_posts",
                }

            if start < 1 or end < start:
                return {
                    "data": {"error": "invalid range: start must be >= 1 and end >= start"},
                    "status": False,
                    "from": "Search.search_posts",
                }

            skip = start - 1
            limit = end - start + 1

            posts = (
                await Post.find(
                    {
                        "$and": [
                            {
                                "$or": [
                                    {"post_fact": {"$regex": keyword, "$options": "i"}},
                                    {"post_research": {"$regex": keyword, "$options": "i"}},
                                ]
                            },
                            {"post_private": False},
                            {"post_blocked": False},
                        ]
                    }
                )
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
                "from": "Search.search_posts",
            }

        except Exception as error:
            log = {
                "data": {"error": str(error)},
                "status": False,
                "from": "Search.search_posts",
            }
            await log_now(log)
            return log