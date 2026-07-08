# app/stage_4/stage_4_man.py

"""Stage 4 orchestrator — generates the post caption from research data."""

from app.stages.stage_4.make_a_meme.meme import meme_text_generate


def start_stage_4(research_data, chosen_topic):
    """Run Stage 4: produce the visible caption text for the post image."""

    print("stage 4")

    meme_text = meme_text_generate(research_data, chosen_topic)

    return meme_text
    

