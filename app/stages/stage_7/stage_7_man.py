# app/stage_7/stage_7_man.py

"""Stage 7 orchestrator — publishes the finished post to the content library."""

from app.stages.stage_7.save_post.save import save_post


async def start_stage_7(chosen_topic, research_data, final_bites, account_id):
    """Run Stage 7: assemble and persist the post record for the web UI."""
    print("stage 7")

    new_post = await save_post(chosen_topic, research_data, final_bites, account_id)

    return str(new_post)

    

