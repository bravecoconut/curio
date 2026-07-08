# app/stage_5/make_prompt_for_image_for_meme/meme_image_prompt.py

"""Build a text-to-image prompt grounded in the topic, caption, and research data."""

from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()
import os

base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
model = os.getenv("RESONNING_MODEL")

import json

import re


def meme_image_prompt_generate(research_data, meme_text, chosen_topic):
    """Return an image-generation prompt describing the post background scene."""

    error = {"error": None}

    try:
        with open("data/json/characters.json") as file:
            personalities = json.load(file)

        characters = """"""

        for person in personalities:
            new_person = f"\"{person['character']}: {person['trope']}\"\n\n"
            characters += new_person

        system_message = "You are an image prompt generator. Follow the instructions in the user message exactly. Output only valid JSON."

        prompt = f"""You are an expert AI image prompt generator for memes.
            Your task is to create a detailed image generation prompt combining a cartoon character with a realistic environment based on an INTERESTING FACT.

            CRITICAL GROUNDING RULE:
            The image must visually depict the scenario described in MEME TEXT.
            However, if MEME TEXT contradicts the FACT DATA, trust the FACT DATA.
            The environment, objects, and setting must come from the FACT DATA — not just from the character's TV show.

            Guidelines:
            1. Select the character named in MEME TEXT.
            2. Place them physically inside a real-world or historically accurate scenario matching the FACT DATA and RESEARCH DATA.
            (e.g. if the fact is about ancient Rome, put them in a historically accurate Roman setting)
            3. The character reacts to or participates in the reality of the fact.
            4. Do NOT include canonical show elements if they don't relates to FACT DATA or RESEARCH DATA (Krabby Patties for SpongeBob, Tom chasing Jerry, etc.)
            or unless the fact data specifically involves those things.
            5. Keep backgrounds simple. Focus on 6-9 key environmental props from the fact.
            6. Include any visual elements that make the absurd fact look hyper-realistic.

            OUTPUT FORMAT:
            Do NOT include markdown formatting.
            Do NOT include conversational filler like 'Here is the prompt'.
            
            Only clear and clean just prompt.
            """

        user_message = f"""# INSTRUCTIONS
        {prompt}

        # CHOSEN TOPIC
        '{chosen_topic}'

        # MEME TEXT (character and action come from here)
        '{meme_text}'

        # RESEARCH DATA (use only the location, environment and props relevant to chosen topic)
        {research_data}

        Output the JSON now. Nothing else."""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        try:
            client = OpenAI(base_url=f"{base_url}/v1", api_key=api_key)
            response_stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                temperature=0.8,  # Moderate temperature for varied but grounded scene descriptions.
            )

            full_reply = ""

            for chunk in response_stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_reply += content

            cleaned_prompt = full_reply.strip()

            return cleaned_prompt

        except Exception as e:
            print(f" -> failed\n : {e}")
            error["error"] = e
            return error

    except Exception as e:
        print(f" -> failed{e}")
        error["error"] = e
        return error
