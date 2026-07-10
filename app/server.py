# app/server.py

from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory,
    render_template,
    make_response,
    redirect,
    url_for
)
from flask_cors import CORS
import os
import re
from app.auth.auth_service import AuthService
from app.auth.session_key import SessionKey
from app.stages.start_stage import start_stages
from app.post.one_post import OnePost
from app.post.explore_posts import ExplorePosts
from app.post.all_posts import AllPosts
from app.user.get_user_account_info import GetUser
from app.user.edit_user import EditUser
from beanie import PydanticObjectId
from app.model.account import Account
from app.db import init_db
from app.user.get_username import GetUsername
from app.post.edit_post import EditPost
from app.search.search import Search

app = Flask(__name__)
CORS(app)



@app.route("/api/auth_service", methods=["POST"])
async def auth_service():
    await init_db()

    data = request.get_json(silent=True)
    if not data or not data.get("email") or not data.get("password"):
        return (
            jsonify(
                {"data": {"error": "email and password are required"}, "status": False}
            ),
            400,
        )

    email = data.get("email")
    password = data.get("password")
    ip = request.remote_addr

    init = AuthService(email=email, password=password, ip=ip)
    work = await init.sign_up_or_login()

    work.pop("from", None)

    status_code = 200 if work.get("status") else 400
    resp = make_response(jsonify(work), status_code)

    if work.get("status"):
        session_id = work["data"]["session_id"]
        resp.set_cookie(
            "sid",
            session_id,
            httponly=True,  # JS can't read it — mitigates XSS token theft
            secure=False,  # only sent over HTTPS — set False only for local http dev
            samesite="Lax",  # CSRF mitigation; use "Strict" if you don't need cross-site nav
            max_age=2592000,  # 30 days, matches your Sessions.expiry_date
        )

    return resp


@app.route("/api/create_post", methods=["POST"])
async def create_post():
    await init_db()
    session_id = request.cookies.get("sid")
    if not session_id:
        return jsonify({"error": "not authenticated"}), 401

    session_result = await SessionKey(session_key=session_id).validate()
    if not session_result.get("status"):
        return jsonify({"error": "invalid or expired session"}), 401

    account_id = session_result["data"]["account_id"]

    result = await start_stages(account_id=account_id)
    result.pop("from", None)

    status_code = 200 if result.get("status") else 400
    return jsonify(result), status_code

@app.route("/static/post-notify-sw.js")
def post_notify_sw():
    response = send_from_directory("static", "post-notify-sw.js")
    response.headers["Service-Worker-Allowed"] = "/"
    return response

@app.route("/api/get_one_post/<post_id>")
async def get_one_post(post_id):
    await init_db()
    if not post_id:
        return jsonify({"error": "post_id is required"}), 400

    viewer_account_id = await _session_account_id()
    one_post = await OnePost().get_one_post(
        post_id, viewer_account_id=viewer_account_id
    )
    one_post.pop("from", None)

    if one_post.get("status"):
        await EditPost(post_id).increment_views()

    status_code = 200 if one_post.get("status") else 404
    return jsonify(one_post), status_code


@app.route("/api/get_all_post", methods=["POST"])
async def get_all_post():
    await init_db()
    data = request.get_json(silent=True) or {}
    start = int(data.get("start", 1))
    end = int(data.get("end", 10))
    session_id = request.cookies.get("sid")

    if not session_id:
        return jsonify({"error": "not authenticated"}), 401

    session_result = await SessionKey(session_key=session_id).validate()
    if not session_result.get("status"):
        return jsonify({"error": "invalid or expired session"}), 401

    account_id = session_result["data"]["account_id"]
    all_posts = await AllPosts(account_id).get_all_posts(start=start, end=end)
    all_posts.pop("from", None)

    status_code = 200 if all_posts.get("status") else 400
    return jsonify(all_posts), status_code


@app.route("/api/get_explore_posts", methods=["POST"])
async def get_explore_posts():
    await init_db()
    data = request.get_json(silent=True) or {}
    start = int(data.get("start", 1))
    end = int(data.get("end", 10))
    session_id = request.cookies.get("sid")

    if not session_id:
        return jsonify({"error": "not authenticated"}), 401

    session_result = await SessionKey(session_key=session_id).validate()
    if not session_result.get("status"):
        return jsonify({"error": "invalid or expired session"}), 401

    explore_posts = await ExplorePosts().get_explore_posts(start=start, end=end)
    explore_posts.pop("from", None)

    # Shuffle posts before sending to frontend
    if explore_posts.get("status") and "posts" in explore_posts.get("data", {}):
        import random
        random.shuffle(explore_posts["data"]["posts"])

    status_code = 200 if explore_posts.get("status") else 400
    return jsonify(explore_posts), status_code


@app.route("/api/post_image/<filename>")
async def results_images(filename):
    await init_db()
    viewer_account_id = await _session_account_id()
    one_post = await OnePost().get_one_post(
        filename, viewer_account_id=viewer_account_id
    )

    if not one_post.get("status"):
        return jsonify({"error": one_post.get("data", {}).get("error", "not found")}), 404

    await EditPost(filename).increment_views()

    folder = os.path.abspath("rage/post")
    return send_from_directory(folder, f"{filename}.png")


@app.route("/api/get_user_all_info")
async def get_user_all_info():
    await init_db()
    session_id = request.cookies.get("sid")

    if not session_id:
        return jsonify({"error": "not authenticated"}), 401

    session_result = await SessionKey(session_key=session_id).validate()
    if not session_result.get("status"):
        return jsonify({"error": "invalid or expired session"}), 401

    account_id = session_result["data"]["account_id"]

    all_info = await GetUser(account_id).get_user_all_info()

    all_info.pop("from", None)

    status_code = 200 if all_info.get("status") else 400
    return jsonify(all_info), status_code


@app.route("/api/get_user_username/<account_id>")
async def get_user_username(account_id):
    await init_db()

    all_info = await GetUser(account_id).get_user_all_info()
    all_info.pop("from", None)

    status_code = 200 if all_info.get("status") else 400
    return jsonify(all_info), status_code



@app.route("/api/user/<username>")
async def get_username_all_info(username):
    await init_db()
    all_info = await GetUsername(username).get_username_all_info()
    all_info.pop("from", None)
    status_code = 200 if all_info.get("status") else 400
    return jsonify(all_info), status_code


@app.route("/api/user/<username>/posts")
async def get_username_all_post(username):
    await init_db()
    data = request.get_json(silent=True) or {}
    start = int(data.get("start") or request.args.get("start", 1))
    end = int(data.get("end") or request.args.get("end", 10))
    viewer_account_id = await _session_account_id()

    all_posts = await GetUsername(username).get_username_all_posts(
        start=start, end=end, viewer_account_id=viewer_account_id
    )
    all_posts.pop("from", None)
    status_code = 200 if all_posts.get("status") else 400
    return jsonify(all_posts), status_code


@app.route("/api/profile_image/<account_id>")
async def profile_image(account_id):
    await init_db()

    all_info = await GetUser(account_id).get_user_all_info()

    if not all_info.get("status"):
        return jsonify({"error": "user not found"}), 404

    avatar_file_name = all_info.get("data", {}).get("user", {}).get("user_avatar")

    if not avatar_file_name or avatar_file_name == "later":
        return jsonify({"error": "no profile image set"}), 404

    folder = os.path.abspath("app/assets/profile")
    return send_from_directory(folder, avatar_file_name)


@app.route("/api/change_name", methods=["POST"])
async def change_name():
    await init_db()
    session_id = request.cookies.get("sid")
    if not session_id:
        return jsonify({"error": "not authenticated"}), 401

    session_result = await SessionKey(session_key=session_id).validate()
    if not session_result.get("status"):
        return jsonify({"error": "invalid or expired session"}), 401

    account_id = session_result["data"]["account_id"]

    data = request.get_json(silent=True) or {}
    new_name = data.get("new_name")
    if not new_name:
        return jsonify({"error": "new_name is required"}), 400

    result = await EditUser(account_id).change_name(new_name)
    result.pop("from", None)
    status_code = 200 if result.get("status") else 400
    return jsonify(result), status_code


@app.route("/api/change_username", methods=["POST"])
async def change_username():
    await init_db()
    session_id = request.cookies.get("sid")
    if not session_id:
        return jsonify({"error": "not authenticated"}), 401

    session_result = await SessionKey(session_key=session_id).validate()
    if not session_result.get("status"):
        return jsonify({"error": "invalid or expired session"}), 401

    account_id = session_result["data"]["account_id"]

    data = request.get_json(silent=True) or {}
    new_username = data.get("new_username")
    if not new_username:
        return jsonify({"error": "new_username is required"}), 400

    result = await EditUser(account_id).change_username(new_username)
    result.pop("from", None)
    status_code = 200 if result.get("status") else 400
    return jsonify(result), status_code


@app.route("/api/increment_quota", methods=["POST"])
async def increment_quota():
    await init_db()
    session_id = request.cookies.get("sid")
    if not session_id:
        return jsonify({"error": "not authenticated"}), 401

    session_result = await SessionKey(session_key=session_id).validate()
    if not session_result.get("status"):
        return jsonify({"error": "invalid or expired session"}), 401

    account_id = session_result["data"]["account_id"]

    result = await EditUser(account_id).increment_quota()
    result.pop("from", None)
    status_code = 200 if result.get("status") else 400
    return jsonify(result), status_code


@app.route("/api/change_profile_image", methods=["POST"])
async def change_profile_image():
    await init_db()
    session_id = request.cookies.get("sid")
    if not session_id:
        return jsonify({"error": "not authenticated"}), 401

    session_result = await SessionKey(session_key=session_id).validate()
    if not session_result.get("status"):
        return jsonify({"error": "invalid or expired session"}), 401

    account_id = session_result["data"]["account_id"]

    if "image" not in request.files:
        return jsonify({"error": "image file is required"}), 400

    image_file = request.files["image"]
    image_bytes = image_file.read()

    # need the account's email to build the filename
    account = await Account.get(PydanticObjectId(account_id))
    if account is None:
        return jsonify({"error": "account not found"}), 404

    result = await EditUser(account_id).change_profile_image(image_bytes, account.email)
    result.pop("from", None)
    status_code = 200 if result.get("status") else 400
    return jsonify(result), status_code


@app.route("/api/toggle_private/<post_id>")
async def toggle_private(post_id):
    await init_db()
    session_id = request.cookies.get("sid")
    if not session_id:
        return jsonify({"error": "not authenticated"}), 401

    session_result = await SessionKey(session_key=session_id).validate()
    if not session_result.get("status"):
        return jsonify({"error": "invalid or expired session"}), 401

    account_id = session_result["data"]["account_id"]

    result = await EditPost(post_id=post_id).toggle_private(account_id=account_id)
    result.pop("from", None)
    status_code = 200 if result.get("status") else 400
    return jsonify(result), status_code



@app.route("/api/search/profiles", methods=["POST"])
async def search_profiles():
    await init_db()

    session_id = request.cookies.get("sid")
    if not session_id:
        return jsonify({"error": "not authenticated"}), 401

    session_result = await SessionKey(session_key=session_id).validate()
    if not session_result.get("status"):
        return jsonify({"error": "invalid or expired session"}), 401

    data = request.get_json(silent=True) or {}
    keyword = data.get("keyword", "")
    start = int(data.get("start", 1))
    end = int(data.get("end", 10))

    result = await Search().search_profiles(keyword, start=start, end=end)
    result.pop("from", None)

    status_code = 200 if result.get("status") else 400
    return jsonify(result), status_code


@app.route("/api/search/posts", methods=["POST"])
async def search_posts():
    await init_db()

    session_id = request.cookies.get("sid")
    if not session_id:
        return jsonify({"error": "not authenticated"}), 401

    session_result = await SessionKey(session_key=session_id).validate()
    if not session_result.get("status"):
        return jsonify({"error": "invalid or expired session"}), 401

    data = request.get_json(silent=True) or {}
    keyword = data.get("keyword", "")
    start = int(data.get("start", 1))
    end = int(data.get("end", 10))

    result = await Search().search_posts(keyword, start=start, end=end)
    result.pop("from", None)

    status_code = 200 if result.get("status") else 400
    return jsonify(result), status_code


# root just funnels to the auth flow
@app.route("/")
async def root():
    return redirect(url_for('auth'))

# auth page — shows login if not authenticated, otherwise sends you to home
@app.route("/auth")
async def auth():
    await init_db()
    session_id = request.cookies.get("sid")
    if session_id:
        session_result = await SessionKey(session_key=session_id).validate()
        if session_result.get("status"):
            return redirect(url_for('home'))

    # not logged in — render the actual login page, don't redirect to self
    return render_template('auth.html')

# home page — requires a valid session
@app.route("/home")
async def home():
    await init_db()
    session_id = request.cookies.get("sid")
    if not session_id:
        return redirect(url_for('auth'))

    session_result = await SessionKey(session_key=session_id).validate()
    if not session_result.get("status"):
        return redirect(url_for('auth'))

    return render_template('home.html')

@app.route("/logout")
async def logout():
    response = redirect(url_for('root'))
    response.delete_cookie('sid')
    return response


OBJECT_ID_PATTERN = re.compile(r"^[a-fA-F0-9]{24}$")


async def _session_account_id():
    session_id = request.cookies.get("sid")
    if not session_id:
        return None

    session_result = await SessionKey(session_key=session_id).validate()
    if not session_result.get("status"):
        return None

    return session_result["data"]["account_id"]


@app.route("/<segment>")
async def dynamic_page(segment):
    await init_db()

    if OBJECT_ID_PATTERN.match(segment):
        viewer_account_id = await _session_account_id()
        one_post = await OnePost().get_one_post(
            segment, viewer_account_id=viewer_account_id
        )
        if not one_post.get("status"):
            return render_template("post.html", post_id=segment, is_own_post=False, not_found=True), 404

        post_account_id = one_post["data"]["post"]["account_id"]
        is_own_post = viewer_account_id == post_account_id

        return render_template(
            "post.html",
            post_id=segment,
            is_own_post=is_own_post,
            not_found=False,
        )

    user_info = await GetUsername(segment).get_username_all_info()
    if not user_info.get("status"):
        return "User not found", 404

    profile_account_id = user_info["data"]["user"]["account_id"]
    viewer_account_id = await _session_account_id()
    is_own_profile = viewer_account_id == profile_account_id

    return render_template(
        "user.html",
        username=segment,
        is_own_profile=is_own_profile,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=False)
