# app/stage_2/save_choosen_topic_in_used_topics/save.py

"""Persist the selected topic so it is excluded from future runs."""

import json


def save_choosen_topic(topic):
    error = {'error': None}

    try:
            
        with open("data/json/used_topics.json") as file:
            used_topics = json.load(file)

        used_topics.append(topic)

        with open("data/json/used_topics.json", "w") as file:
            used_topics = json.dump(used_topics, file)

    except Exception as e:
        error['error'] = e 
        print(e)
        return error