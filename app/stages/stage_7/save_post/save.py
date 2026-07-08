"""Persist a completed post entry to the content library."""

import os
from app.model.account import Post


async def save_post(chosen_topic, research_data, final_bites, account_id):
    error = {'error': None}

    try:
        new_post = Post(
            account_id=account_id,
            post_fact=chosen_topic,
            post_research=research_data,
        )

        await new_post.insert()

        file_name = f"{new_post.id}.png"
        folder = "rage/post"
        os.makedirs(folder, exist_ok=True)

        image_path = os.path.join(folder, file_name)

        with open(image_path, "wb") as f:
            f.write(final_bites)

        new_post.post_file_name = file_name
        await new_post.save()

        return str(new_post.id)

    except Exception as e:
        error['error'] = str(e)
        return error