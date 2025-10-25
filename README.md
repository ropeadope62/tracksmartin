I’m a musician, and to be honest, I find the idea of AI making music kind of unsettling.

It blurs the line between creativity and computation in a way that makes me very uneasy and worried about the future.

But the cat’s out of the bag — this technology exists, and ignoring it doesn’t make it go away.

So I’m exploring it as a technical hobbyist, trying to understand how it works and what it means, without pretending it’s something it’s not.

I hope you are able to use this tool for fun and experimentation, but please remember that true artistry comes from human experience, emotion, and connection — things AI can never replicate.




## TracksMartin - Hits on Demand.

TracksMartin is a straight forward command-line interface (CLI) built with Python's Click library that streamlines AI-powered music creation. It combines the SunoAPI for professional music generation with OpenAI's GPT-4o-mini for intelligent lyric writing, offering both granular control for experienced users and automated workflows for rapid experimentation.

## Key Features


- **Complete Suno API wrapper** - Programmatic access to music creation, extension, stem extraction, and WAV generation with automated task management
- **Genre-specific prompting** - Structured templates for lyrics and style tag generation per genre
- **OpenAI-powered lyric generation** - 12 genre-specific prompt templates (GPT-4o-mini)
- **Lyric refinement pipeline** - Iterative regeneration with feedback loop
- **CLI and interactive modes** - Command-line interface with guided workflow option

## Installation

```bash
pip install -r requirements.txt
```

## Setup

1. Get your API keys:
   - Suno API key from https://sunoapi.com/dashboard/apikey
   - OpenAI API key from https://platform.openai.com/api-keys

2. Create a `.env` file:
```bash
SUNO_API_KEY=your_suno_api_key_here
OPENAI_KEY=sk-your-openai-key-here
```

## Quick Start

### Auto-Generate Everything
```bash
# Create a complete song from just a concept/minimal input. 
python tracksmartin.py create \
  --auto-lyrics \
  --theme "summer love" \
  --genre "pop" \
  --mood "upbeat"
```

### Manual Lyrics with Smart Tags
```bash
# Your lyrics with auto-generated genre tags
python tracksmartin.py create \
  -t "My Song" \
  -f lyrics.txt \
  --genre "rock"
```

### Interactive Mode
```bash
# Guided creation with user prompts
python tracksmartin.py interactive
```

### List Genres & Get Help
```bash
# See all supported genres
python tracksmartin.py genres

# Get genre-specific guidance
python tracksmartin.py genres --genre "hip-hop"
```

## Lyric Auto-Generation

TracksMartin now includes 'guided' lyric generation with **12 genre templates**. Each genre template understands the authentic conventions, structures, and characteristics that make lyrics sound genuine for the music it is generating.
You can bypass these templates by using the `--genre "custom"` option, which uses a generic lyric generation model without genre-specific adjustments. So if you want to generate a thrash-metal headbanger about your pet hamster, you can—and should—do that too.

### Supported Genres

- **Pop** - Catchy hooks, radio-friendly structures
- **Rock** - Powerful imagery, rebellious energy
- **Hip-Hop** - Complex wordplay, internal rhymes, flow
- **Country** - Storytelling with specific details
- **R&B** - Smooth, sensual, emotionally intimate
- **Jazz** - Sophisticated, poetic, timeless
- **Blues** - Raw emotion, AAB structure
- **Electronic** - Minimal, atmospheric, repetitive
- **Folk** - Narrative-driven, authentic voice
- **Metal** - Epic themes, intense imagery
- **Indie** - Introspective, unconventional
- **Reggae** - Positive messages, rhythmic

### Examples by Genre

**Pop Song:**
```bash
python tracksmartin.py create --auto-lyrics --theme "first love" --genre "pop" --mood "sweet"
```

**Rock Anthem:**
```bash
python tracksmartin.py create --auto-lyrics --theme "freedom" --genre "rock" --mood "powerful"
```

**Hip-Hop Track:**
```bash
python tracksmartin.py create --auto-lyrics --theme "city nightlife" --genre "hip-hop" --title "Neon Dreams"
```

**Country Ballad:**
```bash
python tracksmartin.py create --auto-lyrics --theme "coming home" --genre "country" --mood "nostalgic"
```

### Advanced Auto-Lyrics Usage

**Combine auto-lyrics with custom parameters:**
```bash
python tracksmartin.py create \
  --auto-lyrics \
  --theme "freedom and rebellion" \
  --genre "rock" \
  --mood "aggressive" \
  --style-weight 0.8 \
  --weirdness 0.3 \
  --model chirp-v5
```

**Use genre without auto-lyrics (auto-tags only):**
```bash
# Have your own lyrics but want genre-appropriate tags
python tracksmartin.py create \
  -t "My Song" \
  -f my_lyrics.txt \
  --genre "blues"
# Auto-generates: "blues, emotional, soulful"
```

### Interactive Mode with Auto-Lyrics

The interactive mode supports full auto-generation workflow:

```bash
python tracksmartin.py interactive
```

You'll be prompted:
1. "Auto-generate lyrics with AI?" → Choose yes or no
2. Select your genre from the list
3. Enter theme/topic (e.g., "lost love", "celebration")
4. Set mood and length
5. Review the generated lyrics
6. Refine if needed
7. Proceed with music generation
8. Wait for completion and download (MP3 and/or WAV)

### Genre-Specific Tips

**Pop**
- Best themes: Love, relationships, self-empowerment, celebration
- Mood options: upbeat, catchy, melancholic, empowering
- Result: Catchy choruses, simple memorable hooks, radio-friendly structure

**Rock**
- Best themes: Freedom, struggle, rebellion, introspection, power
- Mood options: powerful, aggressive, energetic, raw, emotional
- Result: Strong imagery, guitar-centric arrangements, building momentum

**Hip-Hop**
- Best themes: Street life, success, struggle, storytelling, social commentary
- Mood options: confident, aggressive, smooth, introspective
- Result: Complex wordplay, internal rhymes, strong flow, quotable bars

**Country**
- Best themes: Heartbreak, home, family, rural life, memories
- Mood options: heartfelt, nostalgic, upbeat, melancholic
- Result: Story-driven lyrics, specific details, conversational tone

**R&B**
- Best themes: Romance, intimacy, heartbreak, desire
- Mood options: smooth, sensual, emotional, soulful
- Result: Emotional vulnerability, space for vocal runs, intimate themes

**Jazz**
- Best themes: City life, romance, nostalgia, night time
- Mood options: smooth, sophisticated, bittersweet, mellow
- Result: Literary wordplay, elegant phrasing, timeless quality

**Blues**
- Best themes: Hardship, heartbreak, struggle, resilience
- Mood options: raw, emotional, soulful, gritty
- Result: AAB structure, honest emotion, personal testimony

**Electronic**
- Best themes: Dance, euphoria, freedom, introspection, party
- Mood options: energetic, euphoric, atmospheric, hypnotic
- Result: Minimal lyrics, repetitive hooks, phonetic emphasis

**Folk**
- Best themes: History, community, social issues, nature, journey
- Mood options: authentic, storytelling, reflective, traditional
- Result: Narrative-driven, clear message, organic feel

**Metal**
- Best themes: Darkness, power, mythology, conflict, triumph
- Mood options: aggressive, epic, dark, powerful, intense
- Result: Epic imagery, technical precision, uncompromising energy

**Indie**
- Best themes: Personal introspection, quirky perspectives, artistic concepts
- Mood options: introspective, artistic, unconventional, vulnerable
- Result: Unique structure, literary references, authentic voice

**Reggae**
- Best themes: Unity, peace, love, social justice, spirituality
- Mood options: positive, uplifting, conscious, relaxed
- Result: Message-driven, rhythmic phrasing, call-and-response

### Tips for Best Results

1. **Be specific with themes:** "heartbreak after a long relationship" works better than just "sad"
2. **Match mood to genre:** Each genre has natural moods—don't force "aggressive" on jazz unless you're trying to create the the most horrible sound known to mankind - manic jazz. 
3. **Use length appropriately:**
   - `short`: 1.5-2 min (2 verses, chorus)
   - `medium`: 3 min (3 verses, chorus, bridge) - **recommended**
   - `long`: 4+ min (4 verses, full structure)
4. **Let the AI suggest tags:** The generated tags are genre-optimized for Suno
5. **Experiment:** Try the same theme across different genres to see how the AI adapts!

## Usage

### Quick Start

```bash
# Create a song with custom prompt/lyrics (CLI)
python tracksmartin.py create --title "My Song" --prompt "[Verse]
Lyrics here..." --tags "pop, upbeat"

# Create from description (Python API)
python -c "from tracksmartin_api import TracksMartinClient; api = TracksMartinClient(); \
result = api.create_music_with_description('happy summer song'); \
print(result['task_id'])"

# Check status
python tracksmartin.py get <task_id>

# Interactive mode
python tracksmartin.py interactive
```

### Custom vs No-Custom Mode

**Custom Mode** (`create_music()`):
- Full control over lyrics, title, and style
- Use song structure tags ([Verse], [Chorus], [Bridge])
- Specify exact style tags
- Available via CLI: `python tracksmartin.py create`

**No-Custom Mode** (`create_music_with_description()`):
- Simple description-based generation
- AI creates lyrics and structure automatically
- Great for quick prototypes or instrumental music
- Documentation: https://docs.sunoapi.com/describe-music

## Commands

### `create` - Generate a new song (Custom Mode)

```bash
python tracksmartin.py create [OPTIONS]
```

**Custom mode** allows you to provide specific lyrics, title, and style tags for precise control over the music generation.

**Options:**
- `--title, -t TEXT` - Song title (required)
- `--prompt, -p TEXT` - Lyrics or description for the song (use [Verse], [Chorus], [Bridge] tags for structure)
- `--prompt-file, -f FILE` - Read lyrics/prompt from a file
- `--tags TEXT` - Style tags (e.g., "pop rock, energetic, 120 bpm, female vocals")
- `--negative-tags TEXT` - Tags to avoid in generation
- `--style-weight FLOAT` - Weight for style adherence (0.0 to 1.0)
- `--weirdness FLOAT` - Constraint for weirdness/creativity (0.0 to 1.0)
- `--model, -m [chirp-v3-5|chirp-v4|chirp-v4-5|chirp-v5]` - AI model version (default: chirp-v5)
- `--instrumental` - Generate instrumental only
- `--wait/--no-wait` - Wait for completion (default: yes)
- `--download/--no-download` - Download when complete (default: yes)
- `--output-dir PATH` - Directory to save files (default: current)

**Examples:**

```bash
# Simple creation
python tracksmartin.py create -t "Mambo # 7" -p "[Verse]
I need a little.. I forget the rest
[Chorus]
Oh yeah, Mary all night long!" --tags "pop, happy, 120 bpm"

# From a file
python tracksmartin.py create -t "We Sing Ballads of Yore, Evermore" -f lyrics.txt --tags "power-metal, epic"

# Don't wait for completion
python tracksmartin.py create -t "Background Music" -p "..." --no-wait

# Instrumental only
python tracksmartin.py create -t "Elected Ambient Words 95-04" -p "..." --instrumental --tags "ambient, chill"

# With advanced options
python tracksmartin.py create -t "I got 99 errors but my code ain’t one!" -f lyrics.txt --tags "boom-bap, west coast, old school" --style-weight 0.8 --weirdness 0.3 --negative-tags "electronic, synthesizer"
```

---

### Description-Based Generation (No-Custom Mode)

You can also use the API's **no-custom mode** to generate music from simple descriptions without writing specific lyrics. This is done programmatically using the `create_music_with_description()` method:

```python
from TracksMartin_api import TracksMartinClient

api = TracksMartinClient()

# Generate from a simple description
result = api.create_music_with_description(
    gpt_description_prompt="happy song which is catchy",
    make_instrumental=False,
    mv="chirp-v5"
)

# More detailed description
result = api.create_music_with_description(
    gpt_description_prompt="energetic rock music with powerful guitar solos and epic drum fills",
    make_instrumental=False,
    mv="chirp-v5"
)

# Instrumental ambient music
result = api.create_music_with_description(
    gpt_description_prompt="relaxing ambient music for meditation and yoga",
    make_instrumental=True,
    mv="chirp-v5"
)
```

See `test_description.py` for a complete example with polling and downloading.

---

### `get` - Check generation status

```bash
python tracksmartin.py get TASK_ID [OPTIONS]
```

**Options:**
- `--download/--no-download` - Download if ready
- `--output-dir PATH` - Directory to save files

**Examples:**

```bash
# Check status
python tracksmartin.py get 468d0e42-f7a6-40ce-9a4c-37db56b13b99

# Check and download
python tracksmartin.py get 468d0e42-f7a6-40ce-9a4c-37db56b13b99 --download
```

---

### `extend` - Extend an existing song

```bash
python tracksmartin.py extend CLIP_ID [OPTIONS]
```

**Options:**
- `--lyrics, -l TEXT` - Additional lyrics for the extension
- `--continue-at INTEGER` - Time in seconds to continue from (default: 0)
- `--tags TEXT` - Style tags for the extension

**Examples:**

```bash
python tracksmartin.py extend 26c9c592-0566-46cf-bb71-91ac1deaa7b5 -l "[Outro]
Fading away..."

python tracksmartin.py extend 26c9c592-0566-46cf-bb71-91ac1deaa7b5 --continue-at 60
```

---

### `concat` - Concatenate multiple clips

```bash
python tracksmartin.py concat CLIP_ID1 CLIP_ID2 [CLIP_ID3 ...]
```

**Examples:**

```bash
python tracksmartin.py concat clip1 clip2 clip3
```

---

### `cover` - Create a cover version

```bash
python tracksmartin.py cover CLIP_ID [OPTIONS]
```

**Options:**
- `--prompt, -p TEXT` - Custom lyrics for the cover
- `--title, -t TEXT` - Title for the cover version
- `--tags TEXT` - Style tags (e.g., "pop", "rock")
- `--model, -m TEXT` - Model version (default: chirp-v5)
- `--wait/--no-wait` - Wait for generation to complete (default: no-wait)
- `--download/--no-download` - Download when ready (default: no-download)
- `--output-dir PATH` - Download directory (default: current directory)

**Examples:**

```bash
# Create cover with new style tags
python tracksmartin.py cover 26c9c592-0566-46cf-bb71-91ac1deaa7b5 --tags "jazz, smooth, lounge"

# Create cover with new lyrics and title
python tracksmartin.py cover 26c9c592-0566-46cf-bb71-91ac1deaa7b5 \
  --prompt "[Verse]\nNew lyrics here" \
  --title "My Jazz Cover"

# Create cover and wait for completion with auto-download
python tracksmartin.py cover 26c9c592-0566-46cf-bb71-91ac1deaa7b5 \
  --tags "rock" \
  --wait \
  --download \
  --output-dir ./covers
```

---

### `stems` - Extract stems (separate instruments/vocals)

```bash
python tracksmartin.py stems CLIP_ID [OPTIONS]
```

**Options:**
- `--full` - Extract full stems (vocals, bass, drums, other)
- `--wait` / `--no-wait` - Wait for stems to complete (default: wait)
- `--download` / `--no-download` - Download stems when ready (default: download)
- `--output-dir PATH` - Directory to save stems (default: current directory)

**Examples:**

```bash
# Basic stems (vocals + instrumentals) - auto-wait and download
python tracksmartin.py stems 26c9c592-0566-46cf-bb71-91ac1deaa7b5

# Full stems with custom output directory
python tracksmartin.py stems 26c9c592-0566-46cf-bb71-91ac1deaa7b5 --full --output-dir ./stems

# Start extraction without waiting
python tracksmartin.py stems 26c9c592-0566-46cf-bb71-91ac1deaa7b5 --no-wait

# Wait and download later manually
python tracksmartin.py stems 26c9c592-0566-46cf-bb71-91ac1deaa7b5 --no-download

# Extract all stems and convert to WAV format
python tracksmartin.py stems 26c9c592-0566-46cf-bb71-91ac1deaa7b5 --full --output-dir ./stems
# Then convert each stem to WAV (get stem IDs from the output above)
python tracksmartin.py wav <vocals_stem_id> --download -o ./stems/vocals.wav
python tracksmartin.py wav <bass_stem_id> --download -o ./stems/bass.wav
python tracksmartin.py wav <drums_stem_id> --download -o ./stems/drums.wav
python tracksmartin.py wav <other_stem_id> --download -o ./stems/other.wav
```

**Note:** Stem extraction can take several minutes. By default, the command will poll until completion and automatically download all stems (vocals, instrumentals, bass, drums, other) to the specified output directory. To get WAV format stems, first extract the stems, then use the `wav` command on each stem ID.

---

### `wav` - Get WAV format

```bash
python tracksmartin.py wav CLIP_ID [OPTIONS]
```

**Options:**
- `--download/--no-download` - Download the WAV file
- `--output, -o FILE` - Output filename (default: <clip_id>.wav)

**Examples:**

```bash
# Get WAV URL
python tracksmartin.py wav 26c9c592-0566-46cf-bb71-91ac1deaa7b5

# Download WAV
python tracksmartin.py wav 26c9c592-0566-46cf-bb71-91ac1deaa7b5 --download -o mysong.wav
```

---

### `credits` - Check API credits

```bash
python tracksmartin.py credits
```

---

### `interactive` - Interactive mode

```bash
python tracksmartin.py interactive
```

Start an interactive session with prompts for all parameters.

---

## Advanced Usage

### Piping lyrics from stdin

```bash
cat lyrics.txt | python tracksmartin.py create -t "My Song" -f - --tags "pop"
```

### Batch processing

```powershell
# PowerShell: Create multiple songs
$titles = @("Song1", "Song2", "Song3")
foreach ($title in $titles) {
    python tracksmartin.py create -t $title -p "..." --no-wait
}
```

```bash
# Bash: Create multiple songs
for title in "Song1" "Song2" "Song3"; do
  python tracksmartin.py create -t "$title" -p "..." --no-wait
done
```

### Integration with other tools

```powershell
# PowerShell: Generate lyrics with AI and create song
chatgpt "write lyrics about summer" | Out-File -FilePath lyrics.txt
python tracksmartin.py create -t "Summer Song" -f lyrics.txt --tags "pop, upbeat"
```

```bash
# Bash: Generate lyrics with ChatGPT and create song
chatgpt "write lyrics about summer" > lyrics.txt
python tracksmartin.py create -t "Summer Song" -f lyrics.txt --tags "pop, upbeat"
```

## Workflow Examples

### Workflow 1: Quick Song Creation
```bash
# One command from concept to MP3
python tracksmartin.py create \
  --auto-lyrics \
  --theme "celebrating friendship" \
  --genre "pop" \
  --mood "happy"
```

### Workflow 2: Review Before Generating Music
```bash
# Use interactive mode to review/refine before committing
python tracksmartin.py interactive
# Choose auto-generation
# Review the lyrics
# Refine if needed
# Then proceed with music generation
```

### Workflow 3: Experiment with Different Genres
```bash
# Create the same theme across multiple genres (PowerShell)
$genres = @("pop", "rock", "country", "hip-hop")
foreach ($genre in $genres) {
  python tracksmartin.py create --auto-lyrics --theme "chasing dreams" --genre $genre --no-wait
}
```

```bash
# Bash version
for genre in "pop" "rock" "country" "hip-hop"; do
  python tracksmartin.py create --auto-lyrics --theme "chasing dreams" --genre "$genre" --no-wait
done
```

### Workflow 4: Manual Lyrics with Genre-Optimized Tags
```bash
# Write your own lyrics but get genre-appropriate tags
python tracksmartin.py create \
  -t "My Trucks Got Trucks" \
  -f my_lyrics.txt \
  --genre "country"
# Auto-generates: "country, storytelling, trucks"
```


## Testing & Examples

### Test Lyric Generation
```bash
# Run the test suite to see lyrics generation in action
python test_lyrics_generation.py
```

This demonstrates:
- Basic generation
- Multiple genres with the same theme
- Genre listing and descriptions
- Lyric refinement

### Complete Example Script
```bash
# End-to-end example: auto-generate lyrics and create music
python example_auto_lyrics.py
```

## Global Options

All commands support:
- `--help` - Show help message
- `--version` - Show version

## Output Styling

The CLI uses colored output for better readability:
- **Cyan** - Section headers
- **Green** - Success messages
- **Red** - Error messages  
- **Yellow** - Pending/waiting messages

## Error Handling

The CLI provides clear error messages:

```bash
$ python tracksmartin.py create -t "Test"
Error: Either --prompt or --prompt-file must be provided
```

## Logging

TracksMartin automatically logs all app events and Suno generation details to help you track your music creation history.

### Log Files

- **Location:** `logs/` directory (created automatically)
- **Format:** Daily log files named `tracksmartin_YYYYMMDD.log`
- **Content:** 
  - App events (commands executed, errors, etc.)
  - Generation requests (title, tags, prompts, parameters)
  - API responses (task IDs, clip IDs, URLs)
  - Download history
  - Timestamps for all events

### What Gets Logged

**Creation Events:**
```json
{
  "timestamp": "2025-10-19T10:30:45",
  "event_type": "create_request",
  "data": {
    "title": "My Song",
    "tags": "pop, upbeat",
    "model": "chirp-v5",
    "prompt_length": 245
  }
}
```

**Completion Events:**
```json
{
  "timestamp": "2025-10-19T10:32:15",
  "event_type": "create_complete",
  "data": {
    "task_id": "abc123...",
    "clip_id": "xyz789...",
    "duration": 180,
    "audio_url": "https://...",
    "status": "success"
  }
}
```

### Viewing Logs

```bash
# View today's log
cat logs/tracksmartin_20251019.log

# Search for specific events
grep "create_request" logs/tracksmartin_*.log

# View only errors
grep "ERROR" logs/tracksmartin_*.log

# View generation events
grep "GENERATION_EVENT" logs/tracksmartin_*.log
```

### Log Retention

- Logs are kept indefinitely by default
- Each day creates a new log file
- You can safely delete old log files if needed
- The `logs/` directory is excluded from git (in `.gitignore`)

---

## Tips

1. **Auto-generate lyrics from concepts:**
   ```bash
   python tracksmartin.py create --auto-lyrics --theme "spring break" --genre "pop"
   ```

2. **Use prompt files** for longer songs:
   ```bash
   python tracksmartin.py create -t "Epic Ballad" -f my_lyrics.txt --genre "rock"
   ```

3. **Experiment with genres:**
   ```bash
   # Try the same theme in different genres
   python tracksmartin.py create --auto-lyrics --theme "Teenage Heartbreak" --genre "pop" --no-wait
   python tracksmartin.py create --auto-lyrics --theme "Chasing Dreams" --genre "rock" --no-wait
   python tracksmartin.py create --auto-lyrics --theme "Lifestyle" --genre "hip-hop" --no-wait
   ```

4. **Check credits regularly**:
   ```bash
   python tracksmartin.py credits
   ```

5. **Use --no-wait for batch jobs**:
   ```bash
   python tracksmartin.py create --auto-lyrics --theme "..." --genre "pop" --no-wait
   ```

6. **Save task IDs** for later retrieval:
   ```bash
   python tracksmartin.py create ... --no-wait > task_id.txt
   ```

7. **Review your generation history**:
   ```bash
   grep "create_complete" logs/tracksmartin_*.log | tail -10
   ```

8. **Use interactive mode for refinement:**
   ```bash
   python tracksmartin.py interactive
   # Auto-generate, review, refine, then create
   ```

## Troubleshooting

**API Key Issues:**
```bash
# Make sure .env file exists with both API keys
cat .env
# Should show:
# SUNO_API_KEY=your_suno_key
# OPENAI_KEY=sk-your-openai-key
```

**"OpenAI API key is required" error:**
- Make sure `OPENAI_KEY` is set in your `.env` file
- The key should start with `sk-`
- Required only if using `--auto-lyrics` feature

**"Genre not found" warning:**
- Use `python tracksmartin.py genres` to see supported genres
- The system will still work with custom genres, just without specialized templates

**Lyrics don't match genre well:**
- Try being more specific with mood
- Use the refine feature in interactive mode
- Check the genre description with `tracksmartin genres --genre <name>`

**Tags don't match your vision:**
- You can override suggested tags with `--tags "your, custom, tags"`
- Or combine: use auto-lyrics but provide manual tags

**Import Errors:**
```bash
# Install dependencies
pip install -r requirements.txt
```

**File Not Found:**
```bash
# Use absolute paths or ensure you're in the correct directory
cd /path/to/TracksMartin
python tracksmartin.py ...
```

## Logging & History

**All operations are automatically logged:**
- Location: `logs/tracksmartin_YYYYMMDD.log`
- Includes: Task IDs, Clip IDs, titles, genres, downloads
- Format: Timestamped, human-readable

**View your log:**
```bash
# Today's log
cat logs/tracksmartin_20251020.log

# Search for specific clips
grep "clip_id" logs/*.log

# Find all generated tracks
grep "Creating track" logs/*.log
```

**Important IDs stored in logs:**
- **Task ID**: Used immediately after creation, expires quickly
- **Clip ID**: Permanent identifier for your track, save this!
- All successful creations, downloads, and operations are logged

**Tip:** Keep your log files for permanent record of all your generations and their IDs.

## Examples

### Create a full song with all options

```bash
python tracksmartin.py create \
  --title "The greatest rock song ever made, with a triangle" \
  --prompt-file full_song.txt \
  --tags "epic rock, powerful vocals, 140 bpm, guitar solos, triangle instrument for emphasis" \
  --style-weight 0.8 \
  --weirdness 0.5 \
  --model chirp-v5 \
  --wait \
  --download \
  --output-dir ./music
```

### Quick instrumental creation

```bash
python tracksmartin.py create \
  -t "Chill Beats" \
  -p "[Instrumental]" \
  --instrumental \
  --tags "lo-fi, chill, 85 bpm"
```

### Check and download when ready

```bash
TASK_ID=$(python tracksmartin.py create -t "Song" -p "..." --no-wait | grep "Task created" | cut -d: -f2)
sleep 60
python tracksmartin.py get $TASK_ID --download
```


### API Methods Available

The `TracksMartinClient` class provides the following methods:

**Music Creation:**
- `create_music(prompt, title, tags, style_weight, weirdness_constraint, negative_tags, custom_mode, make_instrumental, mv)` - Custom mode with full control
- `create_music_with_description(gpt_description_prompt, make_instrumental, mv)` - No-custom mode with AI-generated music from descriptions
- `extend_music(clip_id, prompt, continue_at, tags, title)` - Extend existing songs
- `concat_music(clip_ids)` - Concatenate multiple clips
- `cover_music(continue_clip_id, prompt, title, tags, custom_mode, mv)` - Create cover versions with custom lyrics and styles

**Audio Processing:**
- `stems_basic(clip_id)` - Extract basic stems (vocals + instrumentals)
- `stems_full(clip_id)` - Extract full stems (vocals, bass, drums, other)
- `get_wav_url(clip_id)` - Get WAV format URLs
- `download_file(url, output_path, chunk_size)` - Download audio files

**Persona (Voice Cloning):**
- `create_persona(name, description, sample_clip_ids)` - Create a vocal persona from sample clips
- `create_music_with_persona(persona_id, prompt, title, tags, mv)` - Create music using a specific persona

**Utilities:**
- `get_music(task_id)` - Retrieve music by task ID
- `get_credits()` - Check API credits
- `poll_until_complete(task_id, max_attempts, interval, verbose)` - Poll for task completion

## Model Versions

Available AI models (from oldest to newest):
- `chirp-v3-5` - Older version, stable
- `chirp-v4` - Improved quality
- `chirp-v4-5` - Enhanced features
- `chirp-v5` - Latest version with best quality (default)

**Recommendation:** Use `chirp-v5` (the default) for the latest features and best quality.

## Cost Considerations

**Lyrics Generation:**
- Uses OpenAI's API (GPT-4o-mini by default)
- Cost: ~$0.001-0.01 per song
- Required only when using `--auto-lyrics`

**Music Generation:**
- Uses Suno API credits
- Cost varies by your Suno plan

**Total Cost per Song:**
- Without auto-lyrics: Just Suno credits
- With auto-lyrics: OpenAI (~$0.01) + Suno ≈ $0.10-0.30 per song

## See Also

- [Suno API Documentation](https://docs.sunoapi.com/)
  - [Create Music (Custom Mode)](https://docs.sunoapi.com/create-suno-music)
  - [Create Music (No-Custom Mode)](https://docs.sunoapi.com/describe-music)
  - [Extend Music](https://docs.sunoapi.com/extend-suno-music)
  - [Get Credits](https://docs.sunoapi.com/get-credits)
- [Click Documentation](https://click.palletsprojects.com/)
- Example Scripts:


