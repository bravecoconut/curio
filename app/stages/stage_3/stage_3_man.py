# app/stage_3/stage_3_man.py

"""Stage 3 orchestrator — researches the selected topic and returns cleaned copy."""

from app.stages.stage_3.research_on_provided_topic.research import research_for_topic
from app.stages.stage_3.search_on_the_given_sources.scrap import search_for_sources
from app.stages.stage_3.clean_research_data.clean_data import clean_research_data

def start_stage_3(topic):
    """Run Stage 3: gather source material, scrape content, and summarize research."""

    print("stage 3")

    research_data_sources = research_for_topic(topic)

    raw_research_data = search_for_sources(research_data_sources)

    research_data = clean_research_data(raw_research_data)

    return research_data


