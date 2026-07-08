# app/stage_4/make_a_meme/meme.py

"""Generate the post caption text that will appear on the finished image."""

from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()
import os
base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
model = os.getenv("RESONNING_MODEL")

import json


def meme_text_generate(research_data, chosen_topic):
    """Return a single caption line suitable for overlay on the post image."""

    error = {'error': None}

    try:
        with open("data/json/characters.json") as file:
            personalities = json.load(file)

        characters = """"""

        for person in personalities:
            new_person = f"{person['character']}: {person['trope']}\n\n"
            characters += new_person

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
            "[Character] [action that creates ironic contrast] [the uncomfortable implication]\n"
            "The action and the implication must contradict or amplify each other.\n\n"

            "RULES:\n"
            "- Under 20 words\n"
            "- No quotes\n"
            "- Banned words: hilariously, surprisingly, boldly, excitedly, explaining, listing, describing, teaching\n"
            "- Never have the character simply explain or describe the fact — they must LIVE the implication\n"
            "- The edge must come from what the fact MEANS, not what the fact IS\n\n"

    "GOOD EXAMPLES:\n"
            "Fact: Humans share 60% DNA with bananas\n"
            "Bad: SpongeBob explaining that humans share 60% DNA with bananas\n"
            "Good: Homer Simpson eating a banana, technically eating a distant relative\n\n"

            "Fact: 19th century people paid to watch strangers walk for days\n"
            "Bad: SpongeBob excitedly explaining pedestrianism as a sport\n"
            "Good: Homer Simpson refusing to walk to the fridge while his ancestors paid to watch men walk 1000 miles for fun\n\n"

            "Fact: Giraffes only sleep 5 minutes a day\n"
            "Bad: SpongeBob explaining giraffes sleep 5 minutes a day\n"
            "Good: Patrick Star learning giraffes sleep less than him during finals week\n\n"

            "Fact: A 19-sided shape exists only in theory because it has no real world use\n"
            "Bad: Dexter listing 8 random facts about enneadecagons\n"
            "Good: Dexter dedicating his life to a shape no one will ever build or need\n\n"

            "CHARACTER OPTIONS:\n"
            "Homer Simpson → lazy irony, relatable self-destruction\n"
            "Patrick Star → weaponized stupidity that accidentally exposes dark truth\n"
            "Shinchan → childish logic that accidentally reveals the dark truth\n"
            "Bugs Bunny → smug, nonchalant delivery of disturbing facts\n"
            "Dexter → clinical detachment that makes the implication sound worse\n"
            "SpongeBob → naive enthusiasm that makes the dark implication hit harder\n"
            "Johnny Bravo → oblivious confidence accidentally exposing uncomfortable truth\n\n"

            "Output the single caption only. Nothing else."
        )
            

        user_message = f"""# INSTRUCTIONS
        {prompt}

        # THE FACT TO MEME
        {chosen_topic}"""

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

            # Prefer the first line that references a configured character name.
            character_names = [p['character'] for p in personalities]
            lines = cleaned_prompt.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Remove accidental markdown heading prefixes from model output.
                line = line.lstrip('#').strip()
                for name in character_names:
                    if name in line:
                        return line

            # Fall back to the first non-empty line when no character match is found.
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