# app/stage_2/choose_a_topic_to_continue_with/choose.py

"""Select the best post topic from a candidate list using an LLM."""

from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()
import os
base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
model = os.getenv("RESONNING_MODEL")

def choose_single_topic(topics):
    """Return the index of the topic the model selects as most suitable for a post."""

    error = {'error': None}

    # Serialize the candidate list into a numbered index the model can reference.
    topics_for_model = ""

    i = 0
    for topic in topics:
        topic_title = topic.get("topic", " no topic (skip it)")
        used = topic.get("used")

        topics_for_model += f"{i} - {topic_title}\n\n"
        
        i += 1

    system_message = (
        "You are an objective data classification engine sorting through a list of daily facts.\n"
        "Your single task is to identify and select exactly ONE index number representing the most interesting, surprising, or mind-blowing fact that would make a great meme.\n\n"
        
        "CRITICAL TARGET DEFINITIONS:\n"
        "Look for facts that contain the following underlying dynamics:\n"
        "1. Absurd but True: Facts that sound completely ridiculous or counterintuitive but are factually correct.\n"
        "2. Highly Relatable or Comical: Facts about human behavior, everyday objects, or animals that have high comedic potential.\n"
        "3. Mind-Bending Scale: Facts involving massive scale, deep time, or bizarre science that provoke a strong reaction.\n\n"
        
        "OUTPUT MANDATE:\n"
        "1. Provide your step-by-step analytical reasoning path explaining why the chosen fact represents the most meme-worthy and interesting topic.\n"
        "2. Your absolute final line of generation text must follow this exact format: 'WINNER_INDEX: [number]' where [number] is the selected index.\n"
    )



    user_message = topics_for_model

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]


    try:
        client = OpenAI(base_url=f"{base_url}/v1", api_key=api_key)
        response_stream = client.chat.completions.create(
            model=model, 
            messages=messages,
            stream=True,
            temperature=0.2  # Low temperature for deterministic index selection.
        )


        full_reply = ""

        # Accumulate streamed tokens into a single response string.
        for chunk in response_stream:
            content = chunk.choices[0].delta.content
            if content:
                full_reply += content


        # Trim leading and trailing whitespace before parsing.
        cleaned_reply = full_reply.strip()

        # Parse the model's WINNER_INDEX marker from the response text.
        import re

        # Capture the numeric index following the WINNER_INDEX label.
        match = re.search(r"WINNER_INDEX:\s*(\d+)", cleaned_reply)

        if match:
            # Extract the selected list index from the regex capture group.
            numeric_score = int(match.group(1))

            # Reject out-of-range indices to avoid downstream IndexError failures.
            if 0 <= numeric_score < len(topics):
                return numeric_score
            else:
                print(f"Error: Model returned an out-of-bounds index: {numeric_score}")
        else:
            print("Error: Could not find 'WINNER_INDEX: [number]' in the model's text response.")
            return None  # Model response did not contain a valid WINNER_INDEX.
    


    except Exception as e:
        print(f" -> failed\n")
        error['error'] = e 
        return error