# app/user/get_user_account_info.py

from pymongo import AsyncMongoClient
from beanie import init_beanie, PydanticObjectId
from app.model.account import User
from app.log.log import log_now


class GetUser:
    def __init__(self, account_id):
        self.account_id = account_id

    async def get_user_all_info(self):
        try:

            user = await User.find_one(User.account_id == self.account_id)

            if user is None:
                return {
                    "data": {"error": "user not found"},
                    "status": False,
                    "from": "GetUser.get_user_all_info",
                }

            return {
                "data": {"user": user.model_dump(mode="json")},
                "status": True,
                "from": "GetUser.get_user_all_info",
            }

        except Exception as error:
            log = {
                "data": {"error": str(error)},
                "status": False,
                "from": "GetUser.get_user_all_info",
            }
            await log_now(log)
            return log