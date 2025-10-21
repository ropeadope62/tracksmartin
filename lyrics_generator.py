"""
Project: TracksMartin - Hits on Demand.
Module: Lyrics Generator with OpenAI Integration lyrics_generator.py
Author: Dave C. (ropeadope62)
https://github.com/ropeadope62
"""

import os
from typing import Optional, Dict
from dotenv import load_dotenv
from openai import OpenAI
from genre_templates import GENRE_TEMPLATES

class LyricsGeneratorError(Exception):
    """Custom exception for lyrics generation errors"""
    pass


class LyricsGenerator:
    """
    Generates song lyrics using OpenAI's API with genre-specific templates and prompting strategies.
    
    Supports 12 musical genres with specialized templates that define structure patterns,
    lyrical characteristics, and style guidelines. Uses GPT models to generate lyrics
    that conform to genre-specific conventions.
    
    Attributes:
        GENRE_TEMPLATES (dict): Genre configurations with structure, characteristics, and style notes
        api_key (str): OpenAI API key for authentication
        client (OpenAI): Configured OpenAI client instance
    
    Methods:
        generate_lyrics: Creates lyrics from theme, genre, and optional parameters
        refine_lyrics: Modifies existing lyrics based on refinement instructions
        get_genre_info: Retrieves template configuration for a given genre
        list_supported_genres: Returns available genre templates
        get_genre_description: Returns formatted genre information
    
    Raises:
        ValueError: If API key is not provided or found in environment
        LyricsGeneratorError: On API errors or generation failures
    """
    
    # Class attribute - shared across all instances
    GENRE_TEMPLATES = GENRE_TEMPLATES
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the lyrics generator
        
        Args:
            api_key: OpenAI API key. If None, loads from OPENAI_KEY environment variable
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENAI_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Provide it directly or set "
                "OPENAI_KEY environment variable in your .env file."
            )
        
        self.client = OpenAI(api_key=self.api_key)
    
    def get_genre_info(self, genre: str) -> Dict:
        """
        Get genre-specific information for lyric generation
        
        Args:
            genre: Musical genre (e.g., 'pop', 'rock', 'hip-hop')
            
        Returns:
            Dictionary with genre characteristics and guidelines
        """
        genre_lower = genre.lower().strip()
        
        # Handle common variations
        genre_mapping = {
            "hiphop": "hip-hop",
            "hip hop": "hip-hop",
            "rap": "hip-hop",
            "edm": "electronic",
            "dance": "electronic",
            "techno": "electronic",
            "house": "electronic",
            "rnb": "r&b",
            "rhythm and blues": "r&b",
            "alternative": "indie",
            "alt": "indie",
            "heavy metal": "metal",
            "death metal": "metal",
            "power metal": "metal"
        }
        
        normalized_genre = genre_mapping.get(genre_lower, genre_lower)
        
        if normalized_genre in self.GENRE_TEMPLATES:
            return self.GENRE_TEMPLATES[normalized_genre]
        
        # Return generic template for unknown genres
        return {
            "structure": "Verse 1, Chorus, Verse 2, Chorus, Bridge, Chorus",
            "characteristics": [
                "Genre-appropriate themes and language",
                "Clear song structure",
                "Memorable hooks and phrases"
            ],
            "style_notes": f"Write authentic {genre} lyrics following the genre's conventions and characteristics."
        }
    
    def generate_lyrics(
        self,
        theme: str,
        genre: str = "pop",
        title: Optional[str] = None,
        mood: Optional[str] = None,
        length: str = "medium",
        additional_instructions: Optional[str] = None,
        model: str = "gpt-4o-mini"
    ) -> Dict[str, str]:
        """
        Generate song lyrics based on theme and genre
        
        Args:
            theme: Main theme or topic of the song (e.g., "a tough breakup", "overcoming struggles")
            genre: Musical genre (pop, rock, hip-hop, country, r&b, jazz, blues, etc.)
            title: Optional song title (will be generated if not provided)
            mood: Optional mood/tone (e.g., "upbeat", "melancholic", "angry")
            length: Song length - "short" (2 verses), "medium" (3 verses), "long" (4+ verses)
            additional_instructions: Any specific requests or constraints
            model: OpenAI model to use (default: gpt-4o-mini for speed/cost)
            
        Returns:
            Dictionary with 'lyrics', 'title', 'genre', and 'suggested_tags'
        """
        genre_info = self.get_genre_info(genre)
        
        # The lyric generation system prompt
        system_prompt = f"""You are an expert songwriter and lyricist specializing in {genre} music.
You understand the authentic conventions, structures, and emotional language of {genre}.

GENRE CHARACTERISTICS:
{chr(10).join('- ' + char for char in genre_info['characteristics'])}

TYPICAL STRUCTURE:
{genre_info['structure']}

STYLE NOTES:
{genre_info['style_notes']}

Your task is to write authentic, professional-quality {genre} lyrics that would fit naturally in the genre.
Use proper song structure notation: [Verse 1], [Chorus], [Bridge], [Verse 2], etc.
Make the lyrics feel genuine and true to the genre's spirit."""

        length_guide = {
            "short": "2 verses, 1 chorus (repeated), around 1.5-2 minutes",
            "medium": "2-3 verses, chorus, and optional bridge, around 3 minutes",
            "long": "3-4 verses, chorus, bridge, and outro, around 4+ minutes"
        }
        
        user_prompt = f"""Write {genre} song lyrics about: {theme}

Requirements:
- Length: {length_guide.get(length, length_guide['medium'])}
- Genre: {genre}"""
        
        if title:
            user_prompt += f"\n- Use this title: '{title}'"
        else:
            user_prompt += "\n- Create an appropriate title"
        
        if mood:
            user_prompt += f"\n- Mood/Tone: {mood}"
        
        if additional_instructions:
            user_prompt += f"\n- Additional notes: {additional_instructions}"
        
        user_prompt += f"""

Format your response as:
TITLE: [song title]
TAGS: [suggest 3-5 style tags for Suno AI - be specific about tempo, mood, instrumentation]

[Intro]
(if applicable)

[Verse 1]
(lyrics)

[Chorus]
(lyrics)

... etc.

Make it authentic {genre} - not generic. The lyrics should feel like they belong in this genre."""

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,  # Higher creativity for lyrics
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse the response
            lines = content.split('\n')
            parsed_title = None
            parsed_tags = None
            lyrics_lines = []
            
            for line in lines:
                if line.startswith('TITLE:'):
                    parsed_title = line.replace('TITLE:', '').strip()
                elif line.startswith('TAGS:'):
                    parsed_tags = line.replace('TAGS:', '').strip()
                else:
                    lyrics_lines.append(line)
            
            lyrics = '\n'.join(lyrics_lines).strip()
            
            return {
                'lyrics': lyrics,
                'title': parsed_title or title or f"Untitled {genre.title()} Song",
                'genre': genre,
                'suggested_tags': parsed_tags or f"{genre}, original"
            }
            
        except Exception as e:
            raise LyricsGeneratorError(f"Failed to generate lyrics: {str(e)}")
    
    def refine_lyrics(
        self,
        original_lyrics: str,
        refinement_request: str,
        genre: str = "pop",
        model: str = "gpt-4o-mini"
    ) -> str:
        """
        Refine or modify existing lyrics based on feedback
        
        Args:
            original_lyrics: The lyrics to refine
            refinement_request: What to change (e.g., "make the chorus catchier", "add a bridge")
            genre: Musical genre for context
            model: OpenAI model to use
            
        Returns:
            Refined lyrics
        """
        genre_info = self.get_genre_info(genre)
        
        system_prompt = f"""You are an expert {genre} songwriter. 
Refine lyrics while maintaining authentic {genre} style and conventions.

{genre_info['style_notes']}"""

        user_prompt = f"""Original lyrics:
{original_lyrics}

Refinement request: {refinement_request}

Provide the refined lyrics with the same structure notation ([Verse], [Chorus], etc.)."""

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise LyricsGeneratorError(f"Failed to refine lyrics: {str(e)}")
    
    @staticmethod
    def list_supported_genres() -> list:
        """Return list of all supported genres with specialized templates"""
        return sorted(LyricsGenerator.GENRE_TEMPLATES.keys())
    
    @staticmethod
    def get_genre_description(genre: str) -> str:
        """Get a description of a specific genre's characteristics"""
        genre_lower = genre.lower().strip()
        if genre_lower in LyricsGenerator.GENRE_TEMPLATES:
            info = LyricsGenerator.GENRE_TEMPLATES[genre_lower]
            return f"{genre.upper()}\n{info['style_notes']}\n\nStructure: {info['structure']}"
        return f"Genre '{genre}' not found in templates."
