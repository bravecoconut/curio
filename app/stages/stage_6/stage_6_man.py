# app/stage_6/stage_6_man.py

"""Stage 6 orchestrator — composes the final post image with caption overlay."""

from app.stages.stage_6.edit_image.edit import add_meme_text


def start_stage_6(image, text):
    """Run Stage 6: render caption text onto the generated background image."""
    print("stage 6")

    final_bites = add_meme_text(image, text)

    return final_bites

    

