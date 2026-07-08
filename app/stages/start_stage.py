# app/stages/cli_run.py

'''
it handles all the stages work flows
'''
from app.stages.stage_1.stage_1_man import start_stage_1
from app.stages.stage_2.stage_2_man import start_stage_2
from app.stages.stage_3.stage_3_man import start_stage_3
from app.stages.stage_4.stage_4_man import start_stage_4
from app.stages.stage_5.stage_5_man import start_stage_5
from app.stages.stage_6.stage_6_man import start_stage_6
from app.stages.stage_7.stage_7_man import start_stage_7

import json

import os

async def start_stages(account_id):
    searched_topics = start_stage_1()
    print("1")

    chosen_topic_index = start_stage_2(searched_topics)
    if chosen_topic_index is None:
        return {
            "data": {"error": "stage 2 failed to select a topic"},
            "status": False,
            "from": "start_stages",
        }
    
    chosen_topic_text = searched_topics[chosen_topic_index]['topic']
    print("2")


    research_data = start_stage_3(chosen_topic_text)
    print("3")

    
    meme_text = start_stage_4(research_data, chosen_topic_text)
    print("4")


    meme_image = start_stage_5(research_data=research_data, meme_text=meme_text, chosen_topic=chosen_topic_text)
    print("5")


    final_bites = start_stage_6(meme_image, chosen_topic_text)
    print("6")


    # save to db
    new_post = await start_stage_7(chosen_topic_text, research_data, final_bites, account_id)
    print("7")

    return {
        'data' : {'new_post':new_post},
        'status':True,
        'from':'start'
    }

# if __name__ == "__main__":
#     import asyncio
#     result = asyncio.run(start("6a4a85b45245bf32b2eb0a75"))
#     print("RESULT:", result)