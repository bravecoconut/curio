# app/stage_5/make_prompt_for_image_for_meme/meme_image_prompt.py

"""Build a text-to-image prompt grounded in the topic, caption, and research data."""

from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()
import os

base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
model = os.getenv("RESONNING_MODEL")


def meme_image_prompt_generate(research_data, meme_text, chosen_topic):
    """Return an image-generation prompt describing the post background scene."""

    error = {"error": None}

    try:
        system_message = "You are an image prompt generator. Follow the instructions in the user message exactly. Output only valid JSON."

        prompt = f"""You are an expert AI image prompt engineer.
            Your task is to create a detailed image generation prompt depicting a realistic scene based on an INTERESTING FACT.

            CRITICAL GROUNDING RULE:
            The image must visually depict the scenario described in MEME TEXT.
            However, if MEME TEXT contradicts the FACT DATA, trust the FACT DATA.
            The environment, objects, setting, and any subjects must come from the FACT DATA and RESEARCH DATA.

            Guidelines:
            1. Create a realistic scene matching the FACT DATA and RESEARCH DATA.
            2. Place subjects (people, animals, objects) physically inside a real-world or historically accurate scenario.
            3. Subjects should react to or participate in the reality of the fact.
            4. Do NOT include fictional or cartoon elements unless the fact data specifically involves those things.
            5. Keep backgrounds simple. Focus on 6-9 key environmental props from the research data.
            6. Include any visual elements that make the absurd fact look hyper-realistic.
            7. Use photorealistic style with natural lighting and sharp focus.

            OUTPUT FORMAT:
            Do NOT include markdown formatting.
            Do NOT include conversational filler like 'Here is the prompt'.
            Output only clear and clean prompt text.
            """

        user_message = f"""# INSTRUCTIONS
        {prompt}

        # CHOSEN TOPIC
        '{chosen_topic}'

        # MEME TEXT (subject and action come from here)
        '{meme_text}'

        # RESEARCH DATA (use only the location, environment, props, and subjects relevant to chosen topic)
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
