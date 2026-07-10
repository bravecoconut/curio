# app/stage_4/make_a_meme/meme.py

"""Generate the post caption text that will appear on the finished image."""

from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()
import os
base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
model = os.getenv("RESONNING_MODEL")


def meme_text_generate(research_data, chosen_topic):
    """Return a single caption line suitable for overlay on the post image."""

    error = {'error': None}

    try:
        system_message = "You are a dark dank meme headline writer. Follow the instructions in the user message exactly."

        prompt = (
            "Write ONE meme caption. Nothing else.\n\n"

            "THE VIBE:\n"
            "Dark, dry, deadpan. The humor comes from the uncomfortable truth inside the fact. "
            "Not wholesome. Not educational. The caption should make someone exhale sharply through their nose. "
            "If your caption could appear in a school textbook, it is wrong. Start over.\n\n"

            "HOW TO FIND THE JOKE:\n"
            "1. Read the fact\n"
            "2. Ask: what is the most pointless, depressing, or absurd thing "
            "this fact implies about human existence, human effort, or reality itself?\n"
            "3. That implication IS the joke — not the fact itself\n"
            "4. The fact is the setup. The implication is the punchline. Never confuse them.\n\n"

            "FORMAT:\n"
            "[Subject] [action that creates ironic contrast] [the uncomfortable implication]\n"
            "The action and the implication must contradict or amplify each other.\n\n"

            "RULES:\n"
            "- Under 20 words\n"
            "- No quotes\n"
            "- Banned words: hilariously, surprisingly, boldly, excitedly, explaining, listing, describing, teaching\n"
            "- Never simply explain or describe the fact — the caption must LIVE the implication\n"
            "- The edge must come from what the fact MEANS, not what the fact IS\n"
            "- Use subjects derived from the research data or the fact itself\n\n"

            "Output the single caption only. Nothing else."
        )


        user_message = f"""# INSTRUCTIONS
        {prompt}

        # THE FACT TO MEME
        {chosen_topic}

        # RESEARCH DATA
        {research_data}"""

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
                temperature=0.85  # Higher temperature for creative caption variation.
            )


            full_reply = ""

            # Accumulate streamed tokens into a single response string.
            for chunk in response_stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_reply += content


            # Trim leading and trailing whitespace before post-processing.
            cleaned_prompt = full_reply.strip()

            # Return the first non-empty line
            lines = cleaned_prompt.split('\n')
            for line in lines:
                line = line.strip().lstrip('#').strip()
                if line:
                    return line

            return cleaned_prompt



        except Exception as e:
            print(f" -> failed\n : {e}")
            error['error'] = e
            return error

    except Exception as e:
        print(f" -> failed\n : {e}")
        error['error'] = e
        return error