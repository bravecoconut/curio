# app/auth/create_account.py


from app.model.account import Account, User, Sessions
from pymongo.errors import DuplicateKeyError
from app.log.log import log_now
from coolname import generate_slug
import random
import bcrypt
import pydenticon
import io
from PIL import Image

class AuthService:
    def __init__(self, email, password, ip):
        self.email = email
        self.password = password
        self.ip = ip

    async def sign_up_or_login(self):
        save = await self._authenticate_and_create_session()
        return save

    async def _authenticate_and_create_session(self):

        try:

            hashed = bcrypt.hashpw(self.password.encode(), bcrypt.gensalt())
            new_account = Account(email=self.email, password=hashed.decode())

            await new_account.insert()

            # create user and plan
            while True:
                try:



                    # name
                    base_name = generate_slug(3)
                    random_num = random.randint(1000, 9999)
                    generated_username = f"{base_name}{random_num}"

                    # avatar
                    foreground = ["#651FFF", "#00E676", "#FF3D00", "#00B0FF"]
                    background = "rgba(255, 255, 255, 0)"

                    generator = pydenticon.Generator(10, 10, foreground=foreground, background=background)
                    user_data = self.email
                    png_bytes = generator.generate(user_data, 200, 200, output_format="png")

                    # composite onto a padded canvas, centered
                    identicon = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

                    canvas_size = 256
                    padding_ratio = 0.6  # identicon occupies 80% of the canvas, centered
                    inner_size = int(canvas_size * padding_ratio)

                    canvas_background = (0, 0, 0)  # light gray background, adjust to taste
                    canvas = Image.new("RGBA", (canvas_size, canvas_size), canvas_background)

                    resized_identicon = identicon.resize((inner_size, inner_size), Image.LANCZOS)

                    offset = ((canvas_size - inner_size) // 2, (canvas_size - inner_size) // 2)
                    canvas.paste(resized_identicon, offset, resized_identicon)

                    final = canvas.convert("RGB")

                    with open(f"app/assets/profile/{self.email}.png", "wb") as f:
                        final.save(f, format="PNG")

                    print("Success! avatar created.")

                    # save
                    new_user = User(
                        account_id=str(new_account.id),
                        user_name=self.email.split("@")[0],
                        username=generated_username,
                        user_avatar=f"{self.email}.png",
                    )

                    await new_user.insert()

                    break

                except DuplicateKeyError as error:
                    continue

            new_session = Sessions(account_id=str(new_account.id), ip_was=self.ip)

            await new_session.insert()

            log = {
                "data": {"session_id": str(new_session.id)},
                "status": True,
                "from": "CreateAccount.save_credentials",
            }

            return log

        except DuplicateKeyError as error:
            account = await Account.find_one(Account.email == self.email)

            if account is None:
                log = {
                    "data": {"error": "no account"},
                    "status": False,
                    "from": "CreateAccount.save_credentials",
                }

                await log_now(log)

                return log

            if self.email == account.email and bcrypt.checkpw(
                self.password.encode(), account.password.encode()
            ):

                new_session = Sessions(account_id=str(account.id), ip_was=self.ip)

                await new_session.insert()

                log = {
                    "data": {"session_id": str(new_session.id)},
                    "status": True,
                    "from": "CreateAccount.save_credentials",
                }

                return log

            else:

                log = {
                    "data": {"error": "wrong credentials"},
                    "status": False,
                    "from": "CreateAccount.save_credentials",
                }

                await log_now(log)

                return log

        except Exception as error:
            log = {
                "data": {"error": str(error)},
                "status": False,
                "from": "CreateAccount.save_credentials",
            }

            await log_now(log)

            return log
