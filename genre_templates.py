"""
Genre-specific characteristics and best practice prompting templates
Starting with the most popular genres for now which I will refine and expand later on. 
"""
    

GENRE_TEMPLATES = {
        "pop": {
            "structure": "Verse 1, Pre-Chorus, Chorus, Verse 2, Pre-Chorus, Chorus, Bridge, Chorus (repeat)",
            "characteristics": [
                "Catchy, repetitive hooks",
                "Simple, relatable themes (love, relationships, self-empowerment)",
                "3-4 minute length with radio-friendly structure",
                "Emphasis on memorable chorus with singalong quality",
                "Conversational, accessible language",
                "Strong rhythm and cadence for danceability"
            ],
            "style_notes": "Modern pop focuses on immediate emotional connection. Use simple vocabulary, repetition for emphasis, and ensure the chorus is instantly memorable. Themes should be universal and aspirational."
        },
        "rock": {
            "structure": "Intro, Verse 1, Chorus, Verse 2, Chorus, Guitar Solo/Bridge, Chorus, Outro",
            "characteristics": [
                "Powerful, rebellious, or introspective themes",
                "Strong imagery and metaphors",
                "Emphasis on energy and emotional intensity",
                "Guitar-centric arrangements (leave space for solos)",
                "Verses build tension, chorus releases it",
                "Raw, authentic emotional expression"
            ],
            "style_notes": "Rock lyrics should have attitude and edge. Use vivid imagery, avoid being too polite. Themes of freedom, struggle, defiance, or deep emotion work well. Build momentum throughout the song."
        },
        "hip-hop": {
            "structure": "Intro, Verse 1, Hook, Verse 2, Hook, Verse 3, Hook, Outro",
            "characteristics": [
                "Complex wordplay, metaphors, and double meanings",
                "Strong rhythmic flow with attention to syllable count",
                "Internal rhyme schemes (AABB, multis, slant rhymes)",
                "Storytelling or braggadocious themes",
                "Cultural references and authenticity",
                "Punchlines and quotable bars"
            ],
            "style_notes": "Hip-hop demands technical skill. Focus on rhythm, rhyme density, and clever wordplay. Each bar should have purpose. The hook should be catchy but the verses carry the weight. Authenticity and originality are crucial."
        },
        "country": {
            "structure": "Verse 1, Chorus, Verse 2, Chorus, Bridge, Chorus",
            "characteristics": [
                "Storytelling with clear narrative arc",
                "Relatable, down-to-earth imagery",
                "Themes: heartbreak, home, family, rural life, patriotism",
                "Use of specific details (truck models, place names, etc.)",
                "Conversational, honest tone",
                "Often uses second-person 'you' addressing"
            ],
            "style_notes": "Country lyrics tell stories with heart. Use specific, concrete details rather than abstractions. The narrative should feel like a real person's experience. Emotional honesty over complexity."
        },
        "r&b": {
            "structure": "Intro, Verse 1, Pre-Chorus, Chorus, Verse 2, Pre-Chorus, Chorus, Bridge, Chorus (with ad-libs)",
            "characteristics": [
                "Smooth, sensual romantic themes",
                "Vocal runs and melisma opportunities (oh, yeah, baby)",
                "Emotional vulnerability and intimacy",
                "Sophisticated melodic phrasing",
                "Second-person perspective (singing to lover)",
                "Metaphors for love and desire"
            ],
            "style_notes": "R&B is about feeling and groove. Write lyrics that leave space for vocal expression. Use sensory language. Themes should be emotionally intimate. The melody should flow naturally."
        },
        "jazz": {
            "structure": "Flexible - often AABA or verse-chorus, with instrumental breaks",
            "characteristics": [
                "Sophisticated vocabulary and wordplay",
                "Complex emotional themes (bittersweet, nostalgic)",
                "Conversational, sometimes improvisational feel",
                "Classic themes: love, loss, city life, nightlife",
                "Poetic imagery and metaphor",
                "Timeless, elegant phrasing"
            ],
            "style_notes": "Jazz lyrics are literary. Use elevated language, clever turns of phrase, and subtle emotion. Classic jazz standards had sophistication—channel Cole Porter, Ella Fitzgerald era. Quality over quantity."
        },
        "blues": {
            "structure": "12-bar blues pattern (AAB structure in lyrics)",
            "characteristics": [
                "Themes of hardship, heartbreak, struggle, resilience",
                "Call-and-response patterns",
                "Repetition of first line, then response",
                "Raw, honest emotional expression",
                "Use of blue notes and wailing spaces",
                "Personal testimony and life experience"
            ],
            "style_notes": "Blues lyrics are about struggle and survival. Use the classic AAB structure (repeat first line, then answer/resolve). Keep it real and raw. The emotion should feel lived-in and authentic."
        },
        "electronic": {
            "structure": "Minimal vocals, repetitive hooks, emphasis on drops and builds",
            "characteristics": [
                "Sparse, repetitive lyrics",
                "Emphasis on rhythm and phonetics over meaning",
                "Euphoric or introspective themes",
                "Club/party atmosphere or existential reflection",
                "Vocal chops and repeated phrases",
                "Space for instrumental drops"
            ],
            "style_notes": "Electronic music lyrics are minimal and atmospheric. Focus on a few powerful phrases that repeat and build. Think about how the voice becomes an instrument. Less is more."
        },
        "folk": {
            "structure": "Verse 1, Chorus, Verse 2, Chorus, Verse 3, Chorus",
            "characteristics": [
                "Narrative storytelling with moral or message",
                "Acoustic, organic feel",
                "Historical or traditional themes",
                "Social commentary and authenticity",
                "Simple, memorable melodies",
                "Often multiple verses telling a complete story"
            ],
            "style_notes": "Folk tells stories that matter. Use clear narrative, specific details, and authentic voice. Themes of community, history, and human experience. The story is paramount—let it unfold naturally."
        },
        "metal": {
            "structure": "Intro, Verse 1, Pre-Chorus, Chorus, Verse 2, Pre-Chorus, Chorus, Breakdown, Solo, Chorus, Outro",
            "characteristics": [
                "Dark, intense themes (mythology, darkness, struggle, power)",
                "Epic imagery and metaphor",
                "Aggressive, powerful language",
                "Fast-paced delivery or dramatic dynamics",
                "Themes of conflict, darkness, triumph",
                "Technical precision in phrasing"
            ],
            "style_notes": "Metal demands intensity. Use powerful imagery, epic themes, and uncompromising emotion. Whether it's fantasy, darkness, or social critique, go all-in. The energy should match the music."
        },
        "indie": {
            "structure": "Flexible, often unconventional song structures",
            "characteristics": [
                "Introspective, personal themes",
                "Quirky or unconventional perspectives",
                "Literary references and wordplay",
                "Emotional vulnerability with artistic distance",
                "Unique metaphors and imagery",
                "Authenticity over commercial appeal"
            ],
            "style_notes": "Indie embraces creativity and individuality. Don't be afraid of unconventional structure or esoteric references. Balance vulnerability with artistic craft. Authenticity is key."
        },
        "reggae": {
            "structure": "Verse, Chorus, Verse, Chorus, Bridge (often with toasting/rap section), Chorus",
            "characteristics": [
                "Positive, uplifting messages or social commentary",
                "Themes: unity, peace, love, social justice, Rastafarian spirituality",
                "Repetitive, rhythmic phrasing for the groove",
                "Call-and-response elements",
                "Patois/Jamaican dialect considerations",
                "One-drop rhythm consciousness"
            ],
            "style_notes": "Reggae carries a message. Whether spiritual, political, or about love, there's purpose and positivity. The rhythm is crucial—phrase around the one-drop beat. Keep it conscious and uplifting."
        }
    }