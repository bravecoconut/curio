"""Summarize raw scraped research into a single clean paragraph via LLM."""

from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()
import os
base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
model = os.getenv("RESONNING_MODEL")

def clean_research_data(raw_data):
    """Distill scraped source text into concise post-ready research copy."""
    error = {'error': None}

    system_message = (
        "You are an AI data cleaner. Your job is to read the scraped raw data about a specific fact, extract the core truth, and summarize it into a clean, concise, single paragraph. Do not add any filler text or conversational pleasantries."
    )

    user_message = raw_data

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
            temperature=0.2  # Low temperature for factual, consistent summarization.
        )


        full_reply = ""

        # Accumulate streamed tokens into a single response string.
        for chunk in response_stream:
            content = chunk.choices[0].delta.content
            if content:
                full_reply += content


        # Trim leading and trailing whitespace before returning.
        cleaned_reply = full_reply.strip()

        return cleaned_reply
    


    except Exception as e:
        print(f" -> failed\n : {e}")
        error['error'] = e 
        return error