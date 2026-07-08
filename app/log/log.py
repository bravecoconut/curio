# app/log/log.py

from beanie import Document
from pydantic import Field
import time


class Logs(Document):
    data: dict
    status: bool
    from_source: str = Field(..., alias="from")
    created: int = Field(default_factory=time.time)

    class Settings:
        name = "logs"


async def log_now(log_payload: dict):


    new_log = Logs(
        data=log_payload["data"],
        status=log_payload["status"],
        from_source=log_payload["from"],
    )

    await new_log.insert()
    print("Log successfully saved to MongoDB!")

