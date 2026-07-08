# app/stage_3/research_on_provided_topic/research.py

"""Search the web for supplemental sources related to the selected topic."""

from ddgs import DDGS
from ddgs.exceptions import DDGSException
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
database = BASE_DIR.parents[2] / "data" / "db" / "database.db"


def research_for_topic(topic):
    """Query DuckDuckGo for top results matching the topic text."""
    error = {'error': None}


    try:
        
        urls = []

        with DDGS() as ddgs:

                try:

                    # Build the search query from the topic string or dict payload.
                    query_str = topic.get("topic") if isinstance(topic, dict) else topic
                    results = ddgs.text(query_str, region="wt-wt", max_results=5)

                    # Materialize the generator so emptiness can be checked.
                    results_list = list(results)

                    return results_list
    

                except DDGSException as e:
                    # Log provider errors and return them to the caller instead of crashing.
                    print(f"-----Engine skipped phrase: {e}\n")
                    error['error'] = e 
                    return error

    except Exception as e:
        error['error'] = e 
        return error
