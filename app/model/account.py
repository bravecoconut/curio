# app/model/account.py

from beanie import Document
from pydantic import Field, EmailStr
import time
from typing import Optional, Literal
from pymongo import IndexModel, ASCENDING


class User(Document):
    account_id: str
    user_name: str
    username: str
    user_avatar: str
    user_plan: Literal["free", "basic", "pro"] = "free"
    quota_used: int = 0
    quota_limit: int = 5
    user_blocked: bool = False
    user_warnings: int = 0
    date_created: float = Field(default_factory=time.time)
    date_updated: float = Field(default_factory=time.time)

    class Settings:
        name = "users"

        indexes = [IndexModel([("username", ASCENDING)], unique=True)]


class Account(Document):
    email: EmailStr
    password: str
    created_at: float = Field(default_factory=time.time)
    password_updated_at: float = Field(default_factory=time.time)

    class Settings:
        name = "accounts"

        indexes = [IndexModel([("email", ASCENDING)], unique=True)]


class Sessions(Document):
    account_id: str
    logged_at: float = Field(default_factory=time.time)
    ip_was: Optional[str] = None
    expiry_date: float = Field(default_factory=lambda: time.time() + 2592000)


class Post(Document):
    account_id: str
    post_file_name: str = ""
    post_fact: str
    post_research: str
    post_views: int = 0
    post_shares: int = 0
    post_private: bool = False
    post_blocked: bool = False
    date_created: float = Field(default_factory=time.time)
    date_updated: float = Field(default_factory=time.time)

    class Settings:
        name = "posts"
