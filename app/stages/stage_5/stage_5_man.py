# app/stage_5/stage_5_man.py

"""Stage 5 orchestrator — builds an image prompt and generates the post background."""

from app.stages.stage_5.make_prompt_for_image_for_meme.meme_image_prompt import meme_image_prompt_generate
from app.stages.stage_5.make_image_from_prompt.bg_image import meme_image_generate


def start_stage_5(research_data, meme_text, chosen_topic):
    """Run Stage 5: compose an image prompt and generate the background asset."""
    print("stage 5")

    meme_image_prompt = meme_image_prompt_generate(research_data, meme_text, chosen_topic)

    image = meme_image_generate(meme_image_prompt)

    return image

    

