# app/user/edit_user.py

from pymongo.errors import DuplicateKeyError
from app.model.account import User, Account
from app.log.log import log_now
import io
import os
from PIL import Image


def crop_to_square(image: Image.Image) -> Image.Image:
    """
    Crop a PIL Image to a 1:1 (square) aspect ratio, keeping the center.
    """
    width, height = image.size
    side = min(width, height)

    left = (width - side) // 2
    top = (height - side) // 2
    right = left + side
    bottom = top + side

    return image.crop((left, top, right, bottom))


class EditUser:
    def __init__(self, account_id):
        self.account_id = account_id



    async def change_name(self, new_name):
        try:
            user = await User.find_one(User.account_id == self.account_id)
            if user is None:
                return {"data": {"error": "user not found"}, "status": False, "from": "EditUser.change_name"}

            user.user_name = new_name
            await user.save()

            return {"data": {"user_name": user.user_name}, "status": True, "from": "EditUser.change_name"}

        except Exception as error:
            log = {"data": {"error": str(error)}, "status": False, "from": "EditUser.change_name"}
            await log_now(log)
            return log

    async def change_username(self, new_username):
        """Uniqueness is enforced by the DB index on User.username."""
        try:
            user = await User.find_one(User.account_id == self.account_id)
            if user is None:
                return {"data": {"error": "user not found"}, "status": False, "from": "EditUser.change_username"}

            user.username = new_username
            await user.save()

            return {"data": {"username": user.username}, "status": True, "from": "EditUser.change_username"}

        except DuplicateKeyError:
            log = {"data": {"error": "username already taken"}, "status": False, "from": "EditUser.change_username"}
            await log_now(log)
            return log

        except Exception as error:
            log = {"data": {"error": str(error)}, "status": False, "from": "EditUser.change_username"}
            await log_now(log)
            return log

    async def increment_quota(self):
        try:
            user = await User.find_one(User.account_id == self.account_id)
            if user is None:
                return {"data": {"error": "user not found"}, "status": False, "from": "EditUser.increment_quota"}

            if user.quota_used >= user.quota_limit:
                return {
                    "data": {"error": "quota limit reached"},
                    "status": False,
                    "from": "EditUser.increment_quota",
                }

            user.quota_used += 1
            await user.save()

            return {
                "data": {"quota_used": user.quota_used, "quota_limit": user.quota_limit},
                "status": True,
                "from": "EditUser.increment_quota",
            }

        except Exception as error:
            log = {"data": {"error": str(error)}, "status": False, "from": "EditUser.increment_quota"}
            await log_now(log)
            return log




    async def change_profile_image(self, image_bytes, email):
        """Filename is the account's email, e.g. 'test5@mail.com.png'."""
        try:
            user = await User.find_one(User.account_id == self.account_id)
            if user is None:
                return {"data": {"error": "user not found"}, "status": False, "from": "EditUser.change_profile_image"}

            image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
            cropped = crop_to_square(image)

            buf = io.BytesIO()
            cropped.save(buf, format="PNG")
            cropped_bytes = buf.getvalue()

            file_name = f"{email}.png"
            folder = os.path.abspath("app/assets/profile")
            os.makedirs(folder, exist_ok=True)

            with open(os.path.join(folder, file_name), "wb") as f:
                f.write(cropped_bytes)

            user.user_avatar = file_name
            await user.save()

            return {
                "data": {"user_avatar": file_name},
                "status": True,
                "from": "EditUser.change_profile_image",
            }

        except Exception as error:
            log = {"data": {"error": str(error)}, "status": False, "from": "EditUser.change_profile_image"}
            await log_now(log)
            return log