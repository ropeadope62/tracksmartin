"""
Project: TracksMartin - Hits on Demand.
Module: Main module and Command-Line Interface tracksmartin.py
Author: Dave C. (ropeadope62)
https://github.com/ropeadope62
"""

import click
from tracksmartin_api import TracksMartinClient, TracksMartinClientError
from lyrics_generator import LyricsGenerator, LyricsGeneratorError
import sys
import logging
import os
from datetime import datetime


# Setup logging
def setup_logging():
    """Configure logging to file and console"""
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create log filename with date
    log_filename = os.path.join(
        log_dir, 
        f"tracksmartin_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()  # Also log to console at INFO level
        ]
    )
    
    return logging.getLogger(__name__)


logger = setup_logging()


# We need one Click group which will contain all commands
@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(version='2.0.0', prog_name='TracksMartin CLI')
def cli():
    """TracksMartin - Hits on Demand.
    
    \b
    AI-powered music production tool with genre-aware lyric generation.
    
    \b
    Features:
      • Auto-generate lyrics with 12 specialized genre templates
      • Smart style tag suggestions optimized for Suno
      • Full Suno API integration (create, extend, cover, stems)
      • Interactive mode with lyric review and refinement
    
    \b
    Quick Examples:
      # Auto-generate a complete song from concept
      tracksmartin create --auto-lyrics --theme "summer love" --genre "pop"
      
      # List all supported genres
      tracksmartin genres
      
      # Interactive mode with guided creation
      tracksmartin interactive
    
    \b
    Get started: tracksmartin create --help
    """
    pass

# Create a CLI command and add all the options we need for song creation
@cli.command()
@click.option('--title', '-t', help='Title of the song (auto-generated if using --auto-lyrics)')
@click.option('--prompt', '-p', help='Lyrics or description for the song (use [Verse], [Chorus] tags for structure)')
@click.option('--prompt-file', '-f', type=click.File('r'), 
              help='Read lyrics/prompt from a file')
@click.option('--genre', '-g', 
              help='Musical genre (pop, rock, hip-hop, country, r&b, jazz, blues, electronic, folk, metal, indie, reggae). Affects both lyrics generation and music style.')
@click.option('--auto-lyrics', is_flag=True,
              help='Auto-generate lyrics using AI based on theme and genre')
@click.option('--theme', 
              help='Theme/topic for auto-generated lyrics (e.g., "summer romance", "overcoming adversity"). Required with --auto-lyrics')
@click.option('--mood',
              help='Mood/tone for lyrics (e.g., "upbeat", "melancholic", "energetic")')
@click.option('--length',
              type=click.Choice(['short', 'medium', 'long']),
              default='medium',
              help='Song length for auto-generated lyrics')
@click.option('--tags', help='Style tags (e.g., "pop rock, energetic, 120 bpm, female vocals")')
@click.option('--negative-tags', help='Tags to avoid in generation')
@click.option('--style-weight', type=float, 
              help='Weight for style adherence (0.0 to 1.0)')
@click.option('--weirdness', type=float, 
              help='Constraint for weirdness/creativity (0.0 to 1.0)')
@click.option('--model', '-m', 
              type=click.Choice(['chirp-v3-5', 'chirp-v4', 'chirp-v4-5', 'chirp-v5']),
              default='chirp-v5', show_default=True,
              help='AI model version to use')
@click.option('--instrumental', is_flag=True, 
              help='Generate instrumental music only')
@click.option('--wait/--no-wait', default=True, show_default=True,
              help='Wait for generation to complete')
@click.option('--download/--no-download', default=True, show_default=True,
              help='Download the song when complete (requires --wait)')
@click.option('--output-dir', type=click.Path(exists=True, file_okay=False),
              default='.', show_default=True,
              help='Directory to save downloaded files')
def create(title, prompt, prompt_file, genre, auto_lyrics, theme, mood, length,
           tags, negative_tags, style_weight, weirdness, 
           model, instrumental, wait, download, output_dir):
    """Create a new song with AI generation
    
    Examples:
        # With manual lyrics:
        tracksmartin create -t "My Song" -p "[Verse]\\nLyrics here\\n[Chorus]\\nMore lyrics" --genre "pop"
        
        # Auto-generate lyrics:
        tracksmartin create --auto-lyrics --theme "summer love" --genre "pop" --mood "upbeat"
        
        # From a file with genre:
        tracksmartin create -t "My Song" -f lyrics.txt --genre "rock"
    """
    
    # Validate auto-lyrics requirements
    if auto_lyrics:
        if not theme:
            click.echo("Error: --theme is required when using --auto-lyrics", err=True)
            sys.exit(1)
        if not genre:
            click.echo("Error: --genre is required when using --auto-lyrics", err=True)
            sys.exit(1)
    
    # Get prompt from file if provided
    if prompt_file:
        prompt = prompt_file.read()
    
    # Auto-generate lyrics if requested
    if auto_lyrics:
        try:
            click.secho("\n🎵 Generating lyrics with AI...", fg='cyan', bold=True)
            click.echo(f"Theme: {theme}")
            click.echo(f"Genre: {genre}")
            if mood:
                click.echo(f"Mood: {mood}")
            click.echo(f"Length: {length}")
            
            lyrics_gen = LyricsGenerator()
            logger.info(f"Generating lyrics - Theme: {theme}, Genre: {genre}")
            result = lyrics_gen.generate_lyrics(
                theme=theme,
                genre=genre,
                title=title,
                mood=mood,
                length=length
            )
            
            prompt = result['lyrics']
            title = title or result['title']
            suggested_tags = result['suggested_tags']
            
            click.secho("\n✓ Lyrics generated!", fg='green')
            logger.info(f"Lyrics generated - Title: {title}")
            click.echo(f"Title: {title}")
            click.echo(f"Suggested tags: {suggested_tags}")
            click.echo("\nGenerated lyrics:")
            click.echo("=" * 60)
            click.echo(prompt[:500] + ("..." if len(prompt) > 500 else ""))
            click.echo("=" * 60)
            
            # Use suggested tags if user didn't provide custom tags
            if not tags:
                tags = suggested_tags
                click.echo(f"\nUsing suggested tags: {tags}")
            
        except LyricsGeneratorError as e:
            click.secho(f"Error generating lyrics: {e}", fg='red', err=True)
            click.echo("\nMake sure you have set OPENAI_KEY in your .env file")
            sys.exit(1)
    
    # Ensure we have prompt and title
    if not prompt:
        click.echo("Error: Either --prompt, --prompt-file, or --auto-lyrics must be provided", err=True)
        sys.exit(1)
    
    if not title:
        click.echo("Error: --title is required (or use --auto-lyrics to generate)", err=True)
        sys.exit(1)
    
    # If genre is provided but no tags, generate basic genre tags
    if genre and not tags:
        # Basic genre-to-tags mapping
        genre_tags = {
            'pop': 'pop, catchy, melodic',
            'rock': 'rock, energetic, guitar-driven',
            'hip-hop': 'hip-hop, rhythmic, beats',
            'country': 'country, storytelling, acoustic',
            'r&b': 'r&b, smooth, soulful',
            'jazz': 'jazz, sophisticated, improvised',
            'blues': 'blues, emotional, soulful',
            'electronic': 'electronic, synthesized, dance',
            'folk': 'folk, acoustic, narrative',
            'metal': 'metal, heavy, aggressive',
            'indie': 'indie, alternative, artistic',
            'reggae': 'reggae, rhythmic, positive'
        }
        tags = genre_tags.get(genre.lower(), genre)
        click.echo(f"Auto-generated tags from genre: {tags}")
    
    client = TracksMartinClient()
    
    click.secho(f"\nCreating: {title}", fg='cyan', bold=True)
    logger.info(f"Creating track: {title}")
    if genre:
        click.echo(f"Genre: {genre}")
        logger.info(f"Genre: {genre}")
    click.echo(f"Style Tags: {tags or 'default'}")
    logger.info(f"Tags: {tags or 'default'}")
    if negative_tags:
        click.echo(f"Negative tags: {negative_tags}")
    if style_weight is not None:
        click.echo(f"Style weight: {style_weight}")
    if weirdness is not None:
        click.echo(f"Weirdness: {weirdness}")
    click.echo(f"Model: {model}")
    click.echo(f"Mode: {'Instrumental' if instrumental else 'With vocals'}")
    
    if not auto_lyrics:  # Only show preview if not already shown
        click.echo("\nPrompt preview:")
        click.echo("-" * 50)
        click.echo(prompt[:200] + ("..." if len(prompt) > 200 else ""))
        click.echo("-" * 50)
    
    try:
        with click.progressbar(length=1, label='Submitting request') as bar:
            response = client.create_music(
                prompt=prompt,
                title=title,
                tags=tags,
                style_weight=style_weight,
                weirdness_constraint=weirdness,
                negative_tags=negative_tags,
                custom_mode=True,
                make_instrumental=instrumental,
                mv=model
            )
            bar.update(1)
        
        task_id = response['task_id']
        click.secho(f"\nTask created: {task_id}", fg='green')
        logger.info(f"Task created: {task_id}")
        
        if wait:
            click.echo("\nWaiting for generation to complete...")
            
            try:
                clip = client.poll_until_complete(
                    task_id, 
                    max_attempts=20,
                    interval=15,
                    verbose=True
                )
                
                click.secho("\nGeneration complete!", fg='green', bold=True)
                click.echo(f"Clip ID: {clip['clip_id']}")
                logger.info(f"Generation complete - Clip ID: {clip['clip_id']}")
                click.echo(f"Duration: {clip.get('duration')}s")
                click.echo(f"Audio URL: {clip['audio_url']}")
                
                if download and clip.get('audio_url'):
                    filename = client.sanitize_filename(title)
                    mp3_path = f"{output_dir}/{filename}.mp3"
                    
                    with click.progressbar(length=1, label='Downloading MP3') as bar:
                        client.download_file(clip['audio_url'], mp3_path)
                        bar.update(1)
                    
                    click.secho(f"Downloaded: {mp3_path}", fg='green')
                    logger.info(f"Downloaded: {mp3_path}")
                    
            except TracksMartinClientError as e:
                click.secho(f"Generation failed: {e}", fg='red', err=True)
                sys.exit(1)
        else:
            click.echo(f"\nUse 'TracksMartin get {task_id}' to check status")
            
    except TracksMartinClientError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
@click.argument('task_id')
@click.option('--download/--no-download', default=False,
              help='Download the song if ready')
@click.option('--output-dir', type=click.Path(exists=True, file_okay=False),
              default='.', help='Directory to save downloaded files')
def get(task_id, download, output_dir):
    """Get status and details of a generation task"""
    
    client = TracksMartinClient()
    
    click.echo(f"Checking task: {task_id}")
    
    try:
        response = client.get_music(task_id)
        
        if response.get('type') == 'not_ready':
            click.secho("Task not ready yet. Please wait...", fg='yellow')
            return
        
        if response.get('code') == 200 and 'data' in response:
            clips = response['data']
            
            if not clips:
                click.secho("No data available yet", fg='yellow')
                return
            
            click.echo(f"\nFound {len(clips)} clip(s)")
            
            for idx, clip in enumerate(clips, 1):
                state = clip.get('state')
                
                if len(clips) > 1:
                    click.echo(f"\n{'='*50}")
                    click.echo(f"Clip {idx}/{len(clips)}")
                    click.echo(f"{'='*50}")
                
                click.echo(f"Status: {state}")
                click.echo(f"Title: {clip.get('title')}")
                click.echo(f"Clip ID: {clip.get('clip_id')}")
                
                if state == 'succeeded':
                    click.secho("✓ Generation complete!", fg='green', bold=True)
                    click.echo(f"Duration: {clip.get('duration')}s")
                    if clip.get('mv'):
                        click.echo(f"Model: {clip.get('mv')}")
                    if clip.get('tags'):
                        click.echo(f"Tags: {clip.get('tags')}")
                    click.echo(f"\nURLs:")
                    click.echo(f"  Audio: {clip.get('audio_url')}")
                    click.echo(f"  Video: {clip.get('video_url')}")
                    if clip.get('image_url'):
                        click.echo(f"  Image: {clip.get('image_url')}")
                    
                    if download and clip.get('audio_url'):
                        title = clip.get('title', f'output_{idx}')
                        filename = client.sanitize_filename(title)
                        mp3_path = f"{output_dir}/{filename}.mp3"
                        
                        if click.confirm(f'\nDownload to {mp3_path}?'):
                            with click.progressbar(length=1, label='Downloading') as bar:
                                client.download_file(clip['audio_url'], mp3_path)
                                bar.update(1)
                            click.secho(f"Downloaded: {mp3_path}", fg='green')
                
                elif state in ['error', 'failed']:
                    click.secho("✗ Generation failed", fg='red')
                else:
                    click.secho(f"⏳ Still processing: {state}", fg='yellow')
        else:
            click.echo(f"Response: {response}")
            
    except TracksMartinClientError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
@click.argument('clip_id')
@click.option('--lyrics', '-l', default='', help='Additional lyrics for the extension')
@click.option('--continue-at', type=int, default=0,
              help='Time in seconds to continue from')
@click.option('--tags', help='Style tags for the extension')
def extend(clip_id, lyrics, continue_at, tags):
    """Extend an existing song clip"""
    
    client = TracksMartinClient()
    
    click.secho(f"\nExtending clip: {clip_id}", fg='cyan', bold=True)
    
    try:
        response = client.extend_music(
            clip_id=clip_id,
            prompt=lyrics,
            continue_at=continue_at,
            tags=tags
        )
        
        task_id = response['task_id']
        click.secho(f"Extension task created: {task_id}", fg='green')
        click.echo(f"\nUse 'TracksMartin get {task_id}' to check status")
        
    except TracksMartinClientError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
@click.argument('clip_ids', nargs=-1, required=True)
def concat(clip_ids):
    """Concatenate multiple clips into one song
    
    Example: TracksMartin concat clip1 clip2 clip3
    """
    
    if len(clip_ids) < 2:
        click.secho("Error: At least 2 clip IDs required", fg='red', err=True)
        sys.exit(1)
    
    client = TracksMartinClient()
    
    click.secho(f"\nConcatenating {len(clip_ids)} clips", fg='cyan', bold=True)
    
    try:
        response = client.concat_music(list(clip_ids))
        
        task_id = response['task_id']
        click.secho(f"Concatenation task created: {task_id}", fg='green')
        click.echo(f"\nUse 'TracksMartin get {task_id}' to check status")
        
    except TracksMartinClientError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
@click.argument('clip_id')
@click.option('--tags', help='New style tags for the cover version')
def cover(clip_id, tags):
    """Create a cover version of an existing clip"""
    
    client = TracksMartinClient()
    
    click.secho(f"\nCreating cover of: {clip_id}", fg='cyan', bold=True)
    
    try:
        response = client.cover_music(
            clip_id=clip_id,
            new_tags=tags
        )
        
        task_id = response['task_id']
        click.secho(f"Cover task created: {task_id}", fg='green')
        click.echo(f"\nUse 'TracksMartin get {task_id}' to check status")
        
    except TracksMartinClientError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
@click.argument('clip_id')
@click.option('--full', is_flag=True, 
              help='Extract full stems (vocals, bass, drums, other)')
@click.option('--wait/--no-wait', default=True, show_default=True,
              help='Wait for stems extraction to complete')
@click.option('--download/--no-download', default=True, show_default=True,
              help='Download the stems when complete (requires --wait)')
@click.option('--output-dir', type=click.Path(exists=True, file_okay=False),
              default='.', show_default=True,
              help='Directory to save downloaded files')
def stems(clip_id, full, wait, download, output_dir):
    """Extract stems from a clip (separate vocals/instruments)"""
    
    client = TracksMartinClient()
    
    stem_type = "full" if full else "basic"
    click.secho(f"\nExtracting {stem_type} stems from: {clip_id}", 
                fg='cyan', bold=True)
    
    try:
        if full:
            response = client.stems_full(clip_id)
        else:
            response = client.stems_basic(clip_id)
        
        task_id = response['task_id']
        click.secho(f"Stems extraction task created: {task_id}", fg='green')
        logger.info(f"Stems task created: {task_id} (type: {stem_type})")
        
        if wait:
            click.echo("\nWaiting for stems extraction to complete...")
            
            try:
                # Poll for completion - stems might take longer than regular generation
                result = client.poll_until_complete(
                    task_id,
                    max_attempts=30,  # Stems can take longer
                    interval=15,
                    verbose=True
                )
                
                # Result could be a single clip or list of clips (for stems, usually a list)
                if isinstance(result, list):
                    clips = result
                else:
                    clips = [result]
                
                click.secho(f"\n✓ Stems extraction complete! ({len(clips)} file(s))", 
                           fg='green', bold=True)
                logger.info(f"Stems extraction complete - {len(clips)} clips")
                
                # Display info for each stem
                for idx, clip in enumerate(clips, 1):
                    if len(clips) > 1:
                        click.echo(f"\nStem {idx}/{len(clips)}:")
                    click.echo(f"  Title: {clip.get('title')}")
                    click.echo(f"  Clip ID: {clip.get('clip_id')}")
                    click.echo(f"  Duration: {clip.get('duration')}s")
                    click.echo(f"  Audio URL: {clip.get('audio_url')}")
                    
                    if download and clip.get('audio_url'):
                        # Create filename from title or default naming
                        title = clip.get('title', f'stem_{idx}')
                        filename = client.sanitize_filename(title)
                        mp3_path = f"{output_dir}/{filename}.mp3"
                        
                        click.echo(f"  Downloading to: {mp3_path}")
                        with click.progressbar(length=1, label=f'  Downloading stem {idx}') as bar:
                            client.download_file(clip['audio_url'], mp3_path)
                            bar.update(1)
                        click.secho(f"  ✓ Downloaded: {mp3_path}", fg='green')
                        logger.info(f"Downloaded stem: {mp3_path}")
                
            except TracksMartinClientError as e:
                click.secho(f"Stems extraction failed: {e}", fg='red', err=True)
                sys.exit(1)
        else:
            click.echo(f"\nUse 'tracksmartin get {task_id}' to check status")
        
    except TracksMartinClientError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
@click.argument('clip_id')
@click.option('--download/--no-download', default=False,
              help='Download the WAV file')
@click.option('--output', '-o', help='Output filename (default: <clip_id>.wav)')
def wav(clip_id, download, output):
    """Get WAV format URL for a clip"""
    
    client = TracksMartinClient()
    
    click.echo(f"Getting WAV URL for: {clip_id}")
    
    try:
        response = client.get_wav_url(clip_id)
        
        if response.get('message') == 'success':
            wav_url = response['data']['wav_url']
            click.secho(f"\n✓ WAV URL: {wav_url}", fg='green')
            
            if download:
                filename = output or f"{clip_id}.wav"
                
                with click.progressbar(length=1, label='Downloading WAV') as bar:
                    client.download_file(wav_url, filename)
                    bar.update(1)
                
                click.secho(f"Downloaded: {filename}", fg='green')
        else:
            click.secho(f"Failed: {response.get('message')}", fg='red')
            
    except TracksMartinClientError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
def credits():
    """Check remaining API credits"""
    
    client = TracksMartinClient()
    
    try:
        credits_info = client.get_credits()
        
        click.secho("\nAPI Credits", fg='cyan', bold=True)
        click.echo(f"{credits_info}")
        
    except TracksMartinClientError as e:
        click.secho(f"✗ Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
@click.option('--genre', '-g', help='Show detailed description for a specific genre')
def genres(genre):
    """List all supported genres for lyric generation"""
    
    if genre:
        # Show detailed info for specific genre
        try:
            desc = LyricsGenerator.get_genre_description(genre)
            click.secho(f"\n{desc}\n", fg='cyan')
        except Exception as e:
            click.secho(f"Error: {e}", fg='red', err=True)
    else:
        # List all genres
        click.secho("\n📋 Supported Genres for Auto-Lyrics Generation\n", 
                    fg='cyan', bold=True)
        genres_list = LyricsGenerator.list_supported_genres()
        
        for i, g in enumerate(genres_list, 1):
            click.echo(f"  {i:2d}. {g}")
        
        click.echo("\nUse --genre/-g to see detailed info about a specific genre")
        click.echo("Example: tracksmartin genres --genre rock\n")


# Add a quick command for interactive mode
@cli.command()
def interactive():
    """Start an interactive TracksMartin session to create music"""
    
    click.secho("\nTracksMartin - Interactive Mode", 
                fg='cyan', bold=True)
    click.echo("Press Ctrl+C to exit\n")
    
    client = TracksMartinClient()
    
    try:
        # Ask if user wants to auto-generate lyrics
        auto_gen = click.confirm("Auto-generate lyrics with AI?", default=False)
        
        if auto_gen:
            # Auto-generation path
            click.echo("\n" + "="*60)
            click.echo("Available genres:")
            genres = LyricsGenerator.list_supported_genres()
            for i, g in enumerate(genres, 1):
                click.echo(f"  {i}. {g}")
            click.echo("="*60)
            
            genre_input = click.prompt("\nGenre (name or number)", type=str).strip()
            
            # Check if user entered a number
            try:
                genre_num = int(genre_input)
                if 1 <= genre_num <= len(genres):
                    genre = genres[genre_num - 1]
                    click.echo(f"Selected: {genre}")
                else:
                    genre = genre_input
                    click.echo(f"\nNote: '{genre}' is not in the specialized list, but we'll try it anyway!")
            except ValueError:
                # User entered a genre name
                genre = genre_input
                if genre.lower() not in [g.lower() for g in genres]:
                    click.echo(f"\nNote: '{genre}' is not in the specialized list, but we'll try it anyway!")
            
            # Show genre description if available
            try:
                desc = LyricsGenerator.get_genre_description(genre)
                click.echo("\n" + "="*60)
                click.echo(desc)
                click.echo("="*60)
            except Exception:
                pass
            
            theme = click.prompt("\nSong theme/topic (e.g., 'falling in love', 'fame & authenticity')", type=str)
            mood = click.prompt("Mood (e.g., 'upbeat', 'melancholic', 'energetic', 'defiant')", 
                               default="", type=str)
            length = click.prompt("Length", 
                                 type=click.Choice(['short', 'medium', 'long']),
                                 default='medium')
            
            title = click.prompt("Song title (leave blank to auto-generate)", 
                                default="", type=str)
            
            # Generate lyrics
            click.secho("\nGenerating lyrics...", fg='cyan')
            lyrics_gen = LyricsGenerator()
            result = lyrics_gen.generate_lyrics(
                theme=theme,
                genre=genre,
                title=title if title else None,
                mood=mood if mood else None,
                length=length
            )
            
            prompt = result['lyrics']
            title = result['title']
            suggested_tags = result['suggested_tags']
            
            click.secho("\n✓ Lyrics generated!", fg='green', bold=True)
            click.echo(f"Title: {title}")
            click.echo(f"Suggested tags: {suggested_tags}")
            click.echo("\n" + "="*60)
            click.echo(prompt)
            click.echo("="*60)
            
            if not click.confirm("\nProceed with these lyrics?", default=True):
                if click.confirm("Would you like to refine them?", default=True):
                    refinement = click.prompt("What would you like to change?", type=str)
                    click.secho("\n🔄 Refining lyrics...", fg='cyan')
                    prompt = lyrics_gen.refine_lyrics(prompt, refinement, genre)
                    click.echo("\n" + "="*60)
                    click.echo(prompt)
                    click.echo("="*60)
                else:
                    click.echo("Cancelled.")
                    return
            
            # Ask about tags
            if click.confirm(f"\nUse suggested tags: '{suggested_tags}'?", default=True):
                tags = suggested_tags
            else:
                tags = click.prompt("Enter custom style tags", type=str)
        
        else:
            # Manual entry path
            title = click.prompt("Song title", type=str)
            
            click.echo("\n" + "="*60)
            click.echo("Enter lyrics/prompt (press Ctrl+D/Ctrl+Z+Enter when done):")
            click.echo("Tip: Use tags like [Intro], [Verse], [Chorus], [Bridge] for structure")
            click.echo("="*60)
            lyrics_lines = []
            try:
                while True:
                    line = input()
                    lyrics_lines.append(line)
            except EOFError:
                pass
            
            prompt = '\n'.join(lyrics_lines)
            
            click.echo("\n" + "="*60)
            click.echo("Available genres:")
            genres = LyricsGenerator.list_supported_genres()
            for i, g in enumerate(genres, 1):
                click.echo(f"  {i}. {g}")
            click.echo("="*60)
            
            genre_input = click.prompt("\nGenre (optional, name or number)", 
                                default="", type=str).strip()
            
            # Map number to genre name if user entered a number
            genre = ""
            if genre_input:
                try:
                    genre_num = int(genre_input)
                    if 1 <= genre_num <= len(genres):
                        genre = genres[genre_num - 1]
                        click.echo(f"Selected: {genre}")
                    else:
                        genre = genre_input
                except ValueError:
                    # User entered a genre name
                    genre = genre_input
            
            if genre:
                # Auto-suggest tags based on genre
                genre_tags = {
                    'pop': 'pop, catchy, melodic',
                    'rock': 'rock, energetic, guitar-driven',
                    'hip-hop': 'hip-hop, rhythmic, beats',
                    'country': 'country, storytelling, acoustic',
                    'r&b': 'r&b, smooth, soulful',
                    'jazz': 'jazz, sophisticated, improvised',
                    'blues': 'blues, emotional, soulful',
                    'electronic': 'electronic, synthesized, dance',
                    'folk': 'folk, acoustic, narrative',
                    'metal': 'metal, heavy, aggressive',
                    'indie': 'indie, alternative, artistic',
                    'reggae': 'reggae, rhythmic, positive'
                }
                suggested = genre_tags.get(genre.lower(), genre)
                tags = click.prompt(f"Style tags", default=suggested, type=str)
            else:
                click.echo("\n" + "="*60)
                click.echo("Style tags control the musical style, NOT the lyrics content.")
                click.echo("Examples: 'pop rock, energetic, 120 bpm, electric guitar'")
                click.echo("          'jazz, mellow, piano, saxophone'")
                click.echo("="*60)
                tags = click.prompt("\nStyle tags", default="", type=str)
        
        # Advanced options (common for both paths)
        if click.confirm("\nUse advanced options (style weight, weirdness, negative tags)?", 
                        default=False):
            negative_tags = click.prompt("Negative tags (tags to avoid)", 
                                        default="", type=str)
            style_weight = click.prompt("Style weight (0.0-1.0, higher = stricter adherence)", 
                                       type=float, default=None, show_default=False)
            weirdness = click.prompt("Weirdness/creativity (0.0-1.0, higher = more creative)", 
                                    type=float, default=None, show_default=False)
        else:
            negative_tags = None
            style_weight = None
            weirdness = None
        
        instrumental = click.confirm("Generate instrumental only?", default=False)
        
        model = click.prompt(
            "Model version",
            type=click.Choice(['chirp-v3-5', 'chirp-v4', 'chirp-v4-5', 'chirp-v5']),
            default='chirp-v5'
        )
        
        click.echo("\n" + "="*50)
        click.echo("Summary:")
        click.echo(f"  Title: {title}")
        if genre:
            click.echo(f"  Genre: {genre}")
        click.echo(f"  Style Tags: {tags or 'default (AI will choose)'}")
        click.echo(f"  Prompt/Lyrics: {len(prompt)} characters")
        if negative_tags:
            click.echo(f"  Negative tags: {negative_tags}")
        if style_weight is not None:
            click.echo(f"  Style weight: {style_weight}")
        if weirdness is not None:
            click.echo(f"  Weirdness: {weirdness}")
        click.echo(f"  Model: {model}")
        click.echo(f"  Instrumental: {instrumental}")
        click.echo("="*50)
        
        if not click.confirm("\nProceed with generation?"):
            click.echo("Cancelled.")
            return
        
        response = client.create_music(
            prompt=prompt,
            title=title,
            tags=tags,
            style_weight=style_weight,
            weirdness_constraint=weirdness,
            negative_tags=negative_tags,
            custom_mode=True,
            make_instrumental=instrumental,
            mv=model
        )
        
        task_id = response['task_id']
        click.secho(f"\n✓ Task created: {task_id}", fg='green')
        
        if click.confirm("Wait for completion?", default=True):
            clip = client.poll_until_complete(task_id, verbose=True)
            click.secho(f"\n✓ Complete! Audio URL: {clip['audio_url']}", fg='green')
            
            if click.confirm("Download MP3?", default=True):
                filename = client.sanitize_filename(title) + ".mp3"
                client.download_file(clip['audio_url'], filename)
                click.secho(f"✓ Downloaded: {filename}", fg='green')
            
            if click.confirm("Also download as WAV?", default=False):
                clip_id = clip['id']
                click.secho(f"\nGetting WAV URL for clip {clip_id}...", fg='cyan')
                wav_response = client.get_wav(clip_id)
                wav_url = wav_response.get('wav_url')
                
                if wav_url:
                    wav_filename = client.sanitize_filename(title) + ".wav"
                    client.download_file(wav_url, wav_filename)
                    click.secho(f"✓ Downloaded: {wav_filename}", fg='green')
                else:
                    click.secho("✗ WAV URL not available yet", fg='yellow')
        
    except KeyboardInterrupt:
        click.echo("\n\nExiting...")
    except (TracksMartinClientError, LyricsGeneratorError) as e:
        click.secho(f"\n✗ Error: {e}", fg='red', err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
