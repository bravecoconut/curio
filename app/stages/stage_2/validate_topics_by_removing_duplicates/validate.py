# app/stage_2/validate_topics_by_removing_duplicates/validate.py

"""Remove topics that have already been used in prior pipeline runs."""

import json


def validate_topic(topics):
    error = {'error': None}

    try:
        topics_data = topics

        with open("data/json/used_topics.json") as file:
            used_topics = json.load(file)
        


        for used_topic in used_topics:
            if used_topic in topics_data:
                topics_data.remove(used_topic)

        return topics_data
    
    except Exception as e:
        error['error'] = e 
        print(e)
        return error