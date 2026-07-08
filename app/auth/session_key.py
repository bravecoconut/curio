# app/auth/session_key.py

import time
from beanie import PydanticObjectId
from app.model.account import Sessions
from app.log.log import log_now


class SessionKey:
    def __init__(self, session_key):
        self.session_key = session_key

    async def validate(self):
        try:

            try:
                session = await Sessions.get(PydanticObjectId(self.session_key))
            except Exception:
                session = None  # malformed/invalid ObjectId string

            if session is None:
                return {
                    "data": {"error": "session not found"},
                    "status": False,
                    "from": "SessionKey.validate",
                }

            if session.expiry_date < time.time():
                return {
                    "data": {"error": "session expired"},
                    "status": False,
                    "from": "SessionKey.validate",
                }

            return {
                "data": {"account_id": session.account_id},
                "status": True,
                "from": "SessionKey.validate",
            }

        except Exception as error:
            log = {
                "data": {"error": str(error)},
                "status": False,
                "from": "SessionKey.validate",
            }
            await log_now(log)
            return log