# Content Pipeline

CURIO's core product is a **seven-stage AI pipeline** that transforms a scraped daily fact into a finished meme post. The orchestrator is `app/stages/start_stage.py`.

---

## Pipeline Overview

```
start_stages(account_id)
│
├── Stage 1  search_for_topics()          → list of topic dicts
├── Stage 2  validate → choose → save     → chosen topic index
├── Stage 3  research → scrape → clean    → research paragraph
├── Stage 4  meme_text_generate()         → caption string
├── Stage 5  prompt → FLUX image          → PIL Image
├── Stage 6  add_meme_text()              → PNG bytes
└── Stage 7  save_post()                  → MongoDB Post + PNG file
```

Stages 1–6 are **synchronous**. Stage 7 is **async** (database write).

---

## Stage 1 — Topic Discovery

**Manager:** `app/stages/stage_1/stage_1_man.py`  
**Module:** `app/stages/stage_1/search_for_trending_piece/search_topic.py`

### What it does

1. Scrapes **https://www.thefactsite.com/daily-facts/** with browser-like headers.
2. Finds `<p>` tags with CSS classes matching `gb-text-[8 hex chars]`.
3. Filters out boilerplate (attribution, footer text).
4. Keeps facts longer than 30 characters.
5. Writes a dated snapshot to `data/json/latest_topics.json`.
6. Returns a list of `{"topic": "..."}` objects.

### Output example

```json
[
  {"topic": "Humans share 60% DNA with bananas."},
  {"topic": "Monday is the only day of the week with a valid English anagram."}
]
```

---

## Stage 2 — Topic Selection

**Manager:** `app/stages/stage_2/stage_2_man.py`

### Sub-steps

| Step | Module | Purpose |
|------|--------|---------|
| Validate | `validate_topics_by_removing_duplicates/validate.py` | Remove topics already in `data/json/used_topics.json` |
| Choose | `choose_a_topic_to_continue_with/choose.py` | LLM selects best topic index |
| Save | `save_choosen_topic_in_used_topics/save.py` | Append chosen topic to used list |

### LLM selection criteria

The model evaluates topics for:

1. **Absurd but true** — Ridiculous yet factual
2. **Highly relatable or comical** — Human behavior, animals, everyday objects
3. **Mind-bending scale** — Massive scale, deep time, bizarre science

The model must respond with `WINNER_INDEX: [number]` as its final line.

### Failure modes

- All topics already used → empty list → Stage 2 returns `None`
- LLM returns out-of-bounds index → `None`
- Missing `WINNER_INDEX` in response → `None`

---

## Stage 3 — Research

**Manager:** `app/stages/stage_3/stage_3_man.py`

### Sub-steps

| Step | Module | Purpose |
|------|--------|---------|
| Search | `research_on_provided_topic/research.py` | DuckDuckGo text search (top 5 results) |
| Scrape | `search_on_the_given_sources/scrap.py` | Extract article text from result URLs |
| Clean | `clean_research_data/clean_data.py` | LLM summarizes into one clean paragraph |

### Scraping behavior

- Skips JavaScript-only domains (e.g. `msn.com`)
- Strips `script`, `style`, `nav`, `header`, `footer`, `aside`
- Tries common article container CSS classes
- Falls back to `<article>` tag or paragraph density heuristic
- Filters subscription/cookie boilerplate

### Output

A single string paragraph suitable for display in the post metadata panel.

---

## Stage 4 — Caption Generation

**Manager:** `app/stages/stage_4/stage_4_man.py`  
**Module:** `app/stages/stage_4/make_a_meme/meme.py`

### What it does

Generates a **single meme caption** (under 20 words) using character-driven dark humor.

### Character roster

Loaded from `data/json/characters.json`:

| Character | Trope |
|-----------|-------|
| Homer Simpson | Lazy irony, relatable self-destruction |
| Patrick Star | Weaponized stupidity |
| Shinchan | Childish logic revealing dark truth |
| Bugs Bunny | Smug, nonchalant delivery |
| Dexter | Clinical detachment |
| SpongeBob | Naive enthusiasm amplifying dark implication |
| Johnny Bravo | Oblivious confidence |

### Prompt strategy

- Fact is the **setup**; the uncomfortable **implication** is the punchline
- Character must **live** the implication, not explain the fact
- Temperature: `0.85` for creative variation

---

## Stage 5 — Image Generation

**Manager:** `app/stages/stage_5/stage_5_man.py`

### Sub-steps

| Step | Module | Purpose |
|------|--------|---------|
| Prompt | `make_prompt_for_image_for_meme/meme_image_prompt.py` | LLM builds scene description |
| Generate | `make_image_from_prompt/bg_image.py` | API-based image generation |

### Image prompt rules

- Character from caption placed in **fact-accurate environment** (not canonical TV show setting)
- If caption contradicts fact data, **fact data wins**
- 6–9 key environmental props from research
- Hyper-realistic rendering of absurd scenarios

### Model

Uses a self-hosted image generation API endpoint configured via `IMAGE_MODEL_BASE_URL` environment variable. The API accepts JSON with `prompt` and `format` parameters, returning a base64-encoded image.

---

## Stage 6 — Image Composition

**Manager:** `app/stages/stage_6/stage_6_man.py`  
**Module:** `app/stages/stage_6/edit_image/edit.py`

### What it does

1. Converts image to RGBA.
2. Adds a bottom **fade overlay** (100px gradient to black).
3. Creates a **text strip** below the image with wrapped caption.
4. Uses DejaVu Sans Bold, 30px, white text, centered.
5. Returns raw **PNG bytes** (no disk write yet).

### Text wrapping

- Max 55 characters per line via `textwrap.wrap()`.
- Line spacing: 10px, padding: 20px.

---

## Stage 7 — Save & Publish

**Manager:** `app/stages/stage_7/stage_7_man.py`  
**Module:** `app/stages/stage_7/save_post/save.py`

### What it does

1. Creates a `Post` document in MongoDB:
   - `account_id` — owner
   - `post_fact` — chosen topic text
   - `post_research` — cleaned research paragraph
2. Writes PNG to `rage/post/{post_id}.png`.
3. Updates `post_file_name` on the document.
4. Returns the post ObjectId string.

---

## Triggering the Pipeline

### Via API

```http
POST /api/create_post
Cookie: sid=<session_id>
```

### Via UI

Profile page → **create new post** button → Service Worker background job.

### Response

```json
{
  "status": true,
  "data": {
    "new_post": "674a1b2c3d4e5f6789012345"
  }
}
```

---

## Pipeline Data Files

| File | Written by | Purpose |
|------|------------|---------|
| `data/json/latest_topics.json` | Stage 1 | Dated topic snapshots |
| `data/json/used_topics.json` | Stage 2 | Prevents topic reuse |
| `data/json/characters.json` | Manual | Meme character definitions |
| `rage/post/{id}.png` | Stage 7 | Final post image |

---

## Extending the Pipeline

To add a new stage:

1. Create `app/stages/stage_N/` with sub-modules and `stage_N_man.py`.
2. Import and call it from `start_stage.py` between existing stages.
3. Update this document and [Architecture](./02-architecture.md).

To change the fact source, edit `search_topic.py` → `target_url` and parsing logic.

To add characters, edit `data/json/characters.json`.

---

## Related Documents

- [Configuration](./09-configuration.md) — API keys for LLM and Hugging Face
- [API Reference](./05-api-reference.md) — `POST /api/create_post`
