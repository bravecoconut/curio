# app/stage_2/stage_2_man.py

"""Stage 2 orchestrator — validates, selects, and records the post topic."""

import sys
from pathlib import Path

# Resolve project root so `app` imports work regardless of how the process is started.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.stages.stage_2.choose_a_topic_to_continue_with.choose import choose_single_topic
from app.stages.stage_2.validate_topics_by_removing_duplicates.validate import validate_topic
from app.stages.stage_2.save_choosen_topic_in_used_topics.save import save_choosen_topic

import json

from datetime import datetime


def start_stage_2(topics):
    """Run Stage 2: deduplicate topics, select one via LLM, and mark it as used."""
    print("stage 2")

    valid_topics = validate_topic(topics)
    if isinstance(valid_topics, dict) and valid_topics.get('error'):
        print(f"Stage 2 error: {valid_topics['error']}")
        return None

    result = choose_single_topic(valid_topics)
    if isinstance(result, dict) and result.get('error'):
        print(f"Stage 2 error: {result['error']}")
        return None
    if result is None:
        print("Stage 2 error: no topic chosen")
        return None

    choosen_topic = int(result)
    save_result = save_choosen_topic(topics[choosen_topic])
    if isinstance(save_result, dict) and save_result.get('error'):
        print(f"Stage 2 error: {save_result['error']}")
        return None

    return choosen_topic
