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
import time
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
@click.option('--prompt', '-p', help='Additional lyrics for the extension')
@click.option('--title', '-t', help='Title for the extended version')
@click.option('--tags', help='Style tags for the extension')
@click.option('--continue-at', type=int, default=0,
              help='Time in seconds to continue from (default: 0 = end of song)')
@click.option('--model', '-m', default='chirp-v5',
              help='Model version (default: chirp-v5)')
@click.option('--wait/--no-wait', default=False,
              help='Wait for generation to complete')
@click.option('--download/--no-download', default=False,
              help='Download when ready')
@click.option('--output-dir', type=click.Path(), default='.',
              help='Download directory')
def extend(clip_id, prompt, title, tags, continue_at, model, wait, download, output_dir):
    """Extend an existing song clip
    
    \b
    Examples:
      # Extend with new lyrics
      tracksmartin extend <clip_id> --prompt "[Verse 3]\\nNew lyrics here"
      
      # Extend with new title and style
      tracksmartin extend <clip_id> --title "Extended Mix" --tags "energetic"
      
      # Extend from specific timestamp and wait
      tracksmartin extend <clip_id> --continue-at 30 --wait --download
    """
    
    client = TracksMartinClient()
    
    click.secho(f"\nExtending clip: {clip_id}", fg='cyan', bold=True)
    if continue_at > 0:
        click.echo(f"Continue from: {continue_at}s")
    if prompt:
        click.echo(f"Additional lyrics provided")
    if title:
        click.echo(f"Title: {title}")
    if tags:
        click.echo(f"Style tags: {tags}")
    click.echo(f"Model: {model}")
    
    try:
        response = client.extend_music(
            continue_clip_id=clip_id,
            prompt=prompt or "",
            title=title,
            tags=tags,
            continue_at=continue_at,
            mv=model
        )
        
        task_id = response.get('task_id')
        if not task_id:
            click.secho(f"Error: No task_id in response", fg='red', err=True)
            sys.exit(1)
        
        click.secho(f"✓ Extension task created: {task_id}", fg='green')
        logger.info(f"Extension created - clip_id: {clip_id}, task_id: {task_id}")
        
        if wait:
            click.echo("\nWaiting for extension to complete...")
            clip = client.poll_until_complete(task_id, verbose=True)
            click.secho(f"\n✓ Complete! Audio URL: {clip['audio_url']}", fg='green')
            
            if download and clip.get('audio_url'):
                ext_title = title or clip.get('title', f'extended_{clip_id}')
                filename = client.sanitize_filename(ext_title) + ".mp3"
                filepath = f"{output_dir}/{filename}"
                
                client.download_file(clip['audio_url'], filepath)
                click.secho(f"✓ Downloaded: {filepath}", fg='green')
                logger.info(f"Downloaded extension: {filepath}")
        else:
            click.echo(f"\nUse 'tracksmartin get {task_id}' to check status")
        
    except TracksMartinClientError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        logger.error(f"Extension failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument('clip_id')
@click.option('--wait/--no-wait', default=False,
              help='Wait for generation to complete')
@click.option('--download/--no-download', default=False,
              help='Download when ready')
@click.option('--output-dir', type=click.Path(), default='.',
              help='Download directory')
def concat(clip_id, wait, download, output_dir):
    """Get the complete song from an extended clip
    
    After using the extend command, use concat to get the full concatenated result.
    
    \b
    Example workflow:
      1. Extend a clip: tracksmartin extend <clip_id> --prompt "..." --wait
      2. Get the extended clip_id from the result
      3. Concat it: tracksmartin concat <extended_clip_id> --wait --download
    """
    
    client = TracksMartinClient()
    
    click.secho(f"\nGetting concatenated song for clip: {clip_id}", fg='cyan', bold=True)
    
    try:
        response = client.concat_music(clip_id)
        
        task_id = response.get('task_id')
        if not task_id:
            click.secho("Error: No task_id in response", fg='red', err=True)
            sys.exit(1)
        
        click.secho(f"✓ Concatenation task created: {task_id}", fg='green')
        logger.info(f"Concat created - clip_id: {clip_id}, task_id: {task_id}")
        
        if wait:
            click.echo("\nWaiting for concatenation to complete...")
            clip = client.poll_until_complete(task_id, verbose=True)
            click.secho(f"\n✓ Complete! Audio URL: {clip['audio_url']}", fg='green')
            
            if download and clip.get('audio_url'):
                concat_title = clip.get('title', f'concat_{clip_id}')
                filename = client.sanitize_filename(concat_title) + ".mp3"
                filepath = f"{output_dir}/{filename}"
                
                client.download_file(clip['audio_url'], filepath)
                click.secho(f"✓ Downloaded: {filepath}", fg='green')
                logger.info(f"Downloaded concat: {filepath}")
        else:
            click.echo(f"\nUse 'tracksmartin get {task_id}' to check status")
        
    except TracksMartinClientError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        logger.error(f"Concat failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument('clip_id')
@click.option('--prompt', '-p', help='New lyrics for the cover')
@click.option('--title', '-t', help='Title for the cover version')
@click.option('--tags', help='Style tags (e.g., "pop", "rock")')
@click.option('--model', '-m', default='chirp-v5',
              help='Model version (default: chirp-v5)')
@click.option('--wait/--no-wait', default=False,
              help='Wait for generation to complete')
@click.option('--download/--no-download', default=False,
              help='Download when ready')
@click.option('--output-dir', type=click.Path(), default='.',
              help='Download directory')
def cover(clip_id, prompt, title, tags, model, wait, download, output_dir):
    """Create a cover version of an existing clip
    
    \b
    Examples:
      # Create cover with new style tags
      tracksmartin cover <clip_id> --tags "jazz, mellow"
      
      # Create cover with new lyrics
      tracksmartin cover <clip_id> --prompt "[Verse]\\nNew lyrics" 
      
      # Create cover with title and wait for completion
      tracksmartin cover <clip_id> --title "My Cover" --wait --download
    """
    
    client = TracksMartinClient()
    
    click.secho(f"\nCreating cover of: {clip_id}", fg='cyan', bold=True)
    
    # Validate that at least one cover parameter is provided
    if not any([prompt, title, tags]):
        click.secho(
            "Error: You must specify at least one of --prompt, --title, or --tags",
            fg='red', err=True
        )
        click.echo("\nExamples:")
        click.echo("  tracksmartin cover <clip_id> --tags 'rock'")
        click.echo("  tracksmartin cover <clip_id> --prompt '[Verse]\\nLyrics...'")
        click.echo("  tracksmartin cover <clip_id> --title 'My Cover'")
        sys.exit(1)
    
    try:
        response = client.cover_music(
            continue_clip_id=clip_id,
            prompt=prompt,
            title=title,
            tags=tags,
            mv=model
        )
        
        task_id = response.get('task_id')
        if not task_id:
            click.secho(f"Error: No task_id in response", 
                       fg='red', err=True)
            sys.exit(1)
        
        click.secho(f"✓ Cover task created: {task_id}", fg='green')
        logger.info(f"Cover created - clip_id: {clip_id}, task_id: {task_id}")
        
        if wait:
            click.echo("\nWaiting for cover to complete...")
            clip = client.poll_until_complete(task_id, verbose=True)
            click.secho(f"\n✓ Complete! Audio URL: {clip['audio_url']}", 
                       fg='green')
            
            if download and clip.get('audio_url'):
                cover_title = title or clip.get('title', f'cover_{clip_id}')
                filename = client.sanitize_filename(cover_title) + ".mp3"
                filepath = f"{output_dir}/{filename}"
                
                client.download_file(clip['audio_url'], filepath)
                click.secho(f"✓ Downloaded: {filepath}", fg='green')
                logger.info(f"Downloaded cover: {filepath}")
        else:
            click.echo(f"\nUse 'tracksmartin get {task_id}' to check status")
        
    except TracksMartinClientError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        logger.error(f"Cover failed: {e}")
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
@click.argument('clip_id')
@click.option('--download/--no-download', default=False,
              help='Download the MIDI file')
@click.option('--output', '-o', help='Output filename (default: <clip_id>.mid)')
@click.option('--show-instruments', is_flag=True,
              help='Display instrument and note information')
@click.option('--wait/--no-wait', default=True,
              help='Wait for MIDI generation to complete (default: True)')
@click.option('--max-attempts', default=20,
              help='Maximum polling attempts (default: 20)')
@click.option('--poll-interval', default=10,
              help='Seconds between polling attempts (default: 10)')
def midi(clip_id, download, output, show_instruments, wait, max_attempts, poll_interval):
    """Get MIDI format URL and data for a clip
    
    \b
    Works with complete songs or individual stem tracks.
    Returns both a MIDI file URL and detailed instrument/note data.
    
    \b
    Note: MIDI generation is asynchronous and may take time.
    Use --wait to poll until ready (default), or --no-wait for single attempt.
    """
    
    client = TracksMartinClient()
    
    click.echo(f"Getting MIDI data for: {clip_id}")
    
    try:
        if wait:
            click.echo(f"Polling for MIDI (max {max_attempts} attempts, {poll_interval}s interval)...")
            
            # Poll with progress indication
            for attempt in range(1, max_attempts + 1):
                click.echo(f"  Attempt {attempt}/{max_attempts}...", nl=False)
                
                response = client.get_midi(clip_id, max_attempts=1, interval=0)
                
                if response.get('code') == 200 and 'data' in response:
                    data = response['data']
                    midi_url = data.get('midi_url', '')
                    
                    # Check if ready (not "Failed: generating midi...")
                    if midi_url and not 'Failed' in midi_url and not 'generating' in midi_url:
                        click.secho(" ✓ Ready!", fg='green')
                        break
                    else:
                        click.secho(" (still generating)", fg='yellow')
                
                if attempt < max_attempts:
                    time.sleep(poll_interval)
            else:
                click.secho("\n⚠ Max attempts reached. MIDI may still be generating.", fg='yellow')
                click.echo("Try again in a few moments.")
                return
        else:
            response = client.get_midi(clip_id, max_attempts=1, interval=0)
        
        if response.get('code') == 200 and 'data' in response:
            data = response['data']
            midi_url = data.get('midi_url')
            instruments = data.get('instruments', [])
            
            click.secho(f"\n✓ MIDI URL: {midi_url}", fg='green')
            
            if show_instruments and instruments:
                click.echo("\n" + "="*60)
                click.secho("Instrument Information:", fg='cyan', bold=True)
                click.echo("="*60)
                
                for idx, instrument in enumerate(instruments, 1):
                    inst_name = instrument.get('name', 'Unknown')
                    notes = instrument.get('notes', [])
                    click.echo(f"\n{idx}. {inst_name}")
                    click.echo(f"   Notes: {len(notes)}")
                    
                    if notes:
                        # Show first few notes as sample
                        sample_size = min(3, len(notes))
                        click.echo(f"   Sample notes:")
                        for note in notes[:sample_size]:
                            pitch = note.get('pitch')
                            start = note.get('start')
                            end = note.get('end')
                            velocity = note.get('velocity')
                            click.echo(f"     Pitch: {pitch}, "
                                     f"Start: {start:.2f}s, "
                                     f"End: {end:.2f}s, "
                                     f"Velocity: {velocity:.2f}")
                
                click.echo("="*60)
            
            if download and midi_url:
                filename = output or f"{clip_id}.mid"
                
                with click.progressbar(length=1, label='Downloading MIDI') as bar:
                    client.download_file(midi_url, filename)
                    bar.update(1)
                
                click.secho(f"Downloaded: {filename}", fg='green')
                logger.info(f"Downloaded MIDI: {filename}")
        else:
            click.secho(f"Failed: {response.get('message', 'Unknown error')}", 
                       fg='red')
            
    except TracksMartinClientError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
@click.argument('url')
def upload(url):
    """Upload music from a public URL to get a clip_id
    
    \b
    The URL must be publicly accessible (e.g., from cloud storage, CDN, etc.)
    Once uploaded, you'll receive a clip_id that can be used with other commands
    like extend, cover, or stems.
    
    \b
    Examples:
      # Upload from a public URL
      tracksmartin upload https://example.com/my-song.mp3
      
      # Use the returned clip_id with other commands
      tracksmartin extend <clip_id> --prompt "[Verse 3]..." --tags "rock"
      tracksmartin cover <clip_id> --tags "jazz"
      tracksmartin stems <clip_id> --full
    """
    
    client = TracksMartinClient()
    
    click.secho(f"\nUploading music from URL...", fg='cyan', bold=True)
    click.echo(f"URL: {url}")
    
    try:
        with click.progressbar(length=1, label='Uploading') as bar:
            response = client.upload_music(url)
            bar.update(1)
        
        if response.get('code') == 200 and response.get('message') == 'success':
            clip_id = response.get('clip_id')
            click.secho(f"\n✓ Upload successful!", fg='green', bold=True)
            click.echo(f"Clip ID: {clip_id}")
            logger.info(f"Music uploaded - clip_id: {clip_id}, url: {url}")
            
            click.echo("\n" + "="*60)
            click.echo("You can now use this clip_id with other commands:")
            click.echo(f"  • Extend:  tracksmartin extend {clip_id} --prompt '...'")
            click.echo(f"  • Cover:   tracksmartin cover {clip_id} --tags '...'")
            click.echo(f"  • Stems:   tracksmartin stems {clip_id}")
            click.echo(f"  • Get WAV: tracksmartin wav {clip_id}")
            click.echo("="*60)
        else:
            click.secho(f"Upload failed: {response.get('message', 'Unknown error')}", 
                       fg='red', err=True)
            sys.exit(1)
            
    except TracksMartinClientError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        logger.error(f"Upload failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument('clip_id')
@click.argument('name')
def create_persona(clip_id, name):
    """Create a vocal persona from a clip's vocals
    
    \b
    Extract the vocal characteristics from a song to create a reusable persona
    (virtual singer) that can be used to generate new songs with the same voice.
    
    \b
    How it works:
      1. Provide a clip_id from a previously generated song
      2. Give your persona a name
      3. Get back a persona_id that can be used with the 'create' command
    
    \b
    Examples:
      # Create a persona from a clip
      tracksmartin create-persona 4538ed06-ccdd-452d-b90f-c35d29150050 "Smooth Jazz Singer"
      
      # Use the persona_id to create new songs with that voice
      # (Note: Persona usage would be added to the create command)
    
    \b
    Note: The clip must contain vocals (not instrumental-only tracks).
    """
    
    client = TracksMartinClient()
    
    click.secho(f"\nCreating vocal persona from clip...", fg='cyan', bold=True)
    click.echo(f"Clip ID: {clip_id}")
    click.echo(f"Persona Name: {name}")
    
    try:
        with click.progressbar(length=1, label='Creating persona') as bar:
            response = client.create_persona(clip_id, name)
            bar.update(1)
        
        if response.get('code') == 200:
            persona_id = response.get('persona_id')
            click.secho(f"\n✓ Persona created successfully!", fg='green', bold=True)
            click.echo(f"Persona ID: {persona_id}")
            click.echo(f"Name: {name}")
            logger.info(f"Persona created - persona_id: {persona_id}, name: {name}, clip_id: {clip_id}")
            
            click.echo("\n" + "="*60)
            click.secho("What's next?", fg='cyan', bold=True)
            click.echo("You can now use this persona_id to create new songs with")
            click.echo("the same vocal characteristics. The persona captures the")
            click.echo("unique voice, tone, and singing style from the original clip.")
            click.echo("\n" + "="*60)
        else:
            click.secho(f"Failed: {response.get('message', 'Unknown error')}", 
                       fg='red', err=True)
            sys.exit(1)
            
    except TracksMartinClientError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        logger.error(f"Persona creation failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument('persona_id')
@click.option('--prompt', '-p', help='Lyrics for the song')
@click.option('--prompt-file', '-f', type=click.Path(exists=True),
              help='Read lyrics from a file')
@click.option('--title', '-t', help='Title of the song')
@click.option('--tags', help='Style tags (e.g., "pop, upbeat, 120 bpm")')
@click.option('--model', '-m', default='chirp-v5',
              help='Model version (default: chirp-v5)')
@click.option('--wait/--no-wait', default=False,
              help='Wait for generation to complete')
@click.option('--download/--no-download', default=False,
              help='Download when ready')
@click.option('--output-dir', type=click.Path(), default='.',
              help='Download directory')
def use_persona(persona_id, prompt, prompt_file, title, tags, model, wait, download, output_dir):
    """Create music using a persona (virtual singer)
    
    \b
    Use a previously created vocal persona to generate new music with that voice.
    The persona provides the vocal characteristics while you provide new lyrics.
    
    \b
    Examples:
      # Create song with persona
      tracksmartin use-persona c08806c1-34fa-4290-a78d-0c623eb1dd1c \\
        --prompt "[Verse]\\nNew lyrics here\\n[Chorus]\\nCatchy hook" \\
        --title "My New Song" \\
        --tags "pop, upbeat"
      
      # Use lyrics from file
      tracksmartin use-persona <persona_id> \\
        --prompt-file lyrics.txt \\
        --tags "rock, energetic" \\
        --wait --download
      
      # Quick generation with minimal options
      tracksmartin use-persona <persona_id> \\
        -p "[Verse]\\nLyrics..." \\
        --wait
    """
    
    client = TracksMartinClient()
    
    # Read lyrics from file if provided
    if prompt_file:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read()
    
    if not prompt:
        click.secho("Error: Either --prompt or --prompt-file is required", 
                   fg='red', err=True)
        sys.exit(1)
    
    click.secho("\nCreating music with persona...", fg='cyan', bold=True)
    click.echo(f"Persona ID: {persona_id}")
    if title:
        click.echo(f"Title: {title}")
    if tags:
        click.echo(f"Tags: {tags}")
    click.echo(f"Model: {model}")
    
    try:
        response = client.create_music_with_persona(
            persona_id=persona_id,
            prompt=prompt,
            title=title,
            tags=tags,
            mv=model
        )
        
        task_id = response.get('task_id')
        if not task_id:
            click.secho("Error: No task_id in response", fg='red', err=True)
            sys.exit(1)
        
        click.secho(f"✓ Task created: {task_id}", fg='green')
        logger.info(f"Persona music - persona_id: {persona_id}, task_id: {task_id}")
        
        if wait:
            click.echo("\nWaiting for generation to complete...")
            clip = client.poll_until_complete(task_id, verbose=True)
            click.secho(f"\n✓ Complete! Audio URL: {clip['audio_url']}", fg='green')
            
            if download and clip.get('audio_url'):
                song_title = title or clip.get('title', f'persona_{task_id}')
                filename = client.sanitize_filename(song_title) + ".mp3"
                filepath = f"{output_dir}/{filename}"
                
                client.download_file(clip['audio_url'], filepath)
                click.secho(f"✓ Downloaded: {filepath}", fg='green')
                logger.info(f"Downloaded: {filepath}")
        else:
            click.echo("\nTo check status later:")
            click.echo(f"  python tracksmartin.py get {task_id}")
            click.echo("\nTo download when ready:")
            click.echo(f"  python tracksmartin.py get {task_id} --download")
    
    except TracksMartinClientError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        logger.error(f"Persona music creation failed: {e}")
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
            
            # For manual path, set suggested_tags if genre is known
            if genre:
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
                suggested_tags = genre_tags.get(genre.lower(), genre)
            else:
                suggested_tags = ""
        
        # ========== MUSICAL STYLE CONFIGURATION (Common for both paths) ==========
        click.echo("\n" + "="*60)
        click.secho("MUSICAL STYLE CONFIGURATION", fg='cyan', bold=True)
        click.echo("="*60)
        
        # 1. STYLE TAGS (Most Important!)
        click.echo("\nStyle tags define the MUSICAL SOUND (not lyric content)")
        click.echo("\nWhat to include in style tags:")
        click.echo("  • Genre/subgenre (indie rock, synthwave, trap, etc.)")
        click.echo("  • Instruments (electric guitar, synthesizer, 808 drums)")
        click.echo("  • Tempo (120 bpm, slow tempo, uptempo)")
        click.echo("  • Vocal style (female vocals, raspy voice, smooth)")
        click.echo("  • Production (lo-fi, polished, raw, reverb)")
        click.echo("  • Energy/mood (energetic, chill, aggressive, mellow)")
        
        click.echo("\nExample tag combinations:")
        click.echo("  • 'indie rock, electric guitar, energetic, 140 bpm'")
        click.echo("  • 'synthwave, retro, 80s, synthesizer, drums, 128 bpm'")
        click.echo("  • 'lo-fi hip-hop, jazz samples, mellow, vinyl crackle, 90 bpm'")
        click.echo("  • 'acoustic folk, fingerpicking, intimate, female vocals'")
        click.echo("  • 'metal, aggressive, distorted guitar, double bass, 160 bpm'")
        
        if suggested_tags:
            click.echo(f"\nSuggested tags: {suggested_tags}")
            if click.confirm(f"Use suggested tags?", default=True):
                tags = suggested_tags
            else:
                tags = click.prompt("Enter your style tags (comma-separated)", type=str)
        else:
            tags = click.prompt("\nEnter style tags (comma-separated)", type=str)
        
        # 2. NEGATIVE TAGS
        click.echo("\n" + "-"*60)
        if click.confirm("Specify sounds to AVOID?", default=False):
            click.echo("Examples: 'no autotune', 'no heavy drums', 'no synthesizer'")
            negative_tags = click.prompt("Negative tags (comma-separated)", 
                                        default="", type=str)
        else:
            negative_tags = None
        
        # 3. VOCAL STYLE (before instrumental choice)
        click.echo("\n" + "-"*60)
        instrumental = click.confirm("Generate instrumental version (no vocals)?", 
                                    default=False)
        
        if not instrumental:
            vocal_style = click.prompt(
                "Vocal style (optional - e.g., 'raspy', 'smooth', 'powerful')",
                default="",
                type=str
            )
            if vocal_style:
                tags = f"{tags}, {vocal_style} vocals"
        
        # 4. STYLE ADHERENCE
        click.echo("\n" + "-"*60)
        click.secho("Style Weight:", fg='yellow', bold=True)
        click.echo("How strictly should the AI follow your style tags?")
        click.echo("  0.0-0.3 = Very loose (AI adds creative interpretation)")
        click.echo("  0.4-0.6 = Balanced (recommended)")
        click.echo("  0.7-1.0 = Strict adherence to your exact tags")
        click.echo("-"*60)
        
        if click.confirm("Set custom style weight?", default=False):
            style_weight = click.prompt("Style weight (0.0-1.0)", 
                                       type=float, default=0.5)
        else:
            style_weight = None
        
        # 5. CREATIVITY/WEIRDNESS
        click.echo("\n" + "-"*60)
        click.secho("Weirdness/Creativity:", fg='yellow', bold=True)
        click.echo("How experimental should the sound be?")
        click.echo("  0.0-0.3 = Conventional, familiar structures")
        click.echo("  0.4-0.6 = Balanced creativity")
        click.echo("  0.7-1.0 = Experimental, unusual, avant-garde")
        click.echo("-"*60)
        
        if click.confirm("Set custom weirdness level?", default=False):
            weirdness = click.prompt("Weirdness (0.0-1.0)", 
                                    type=float, default=0.3)
        else:
            weirdness = None
        
        # 6. MODEL VERSION
        click.echo("\n" + "-"*60)
        model = click.prompt(
            "Model version",
            type=click.Choice(['chirp-v3-5', 'chirp-v4', 'chirp-v4-5', 'chirp-v5']),
            default='chirp-v5'
        )
        
        # SUMMARY
        click.echo("\n" + "="*60)
        click.secho("GENERATION SUMMARY", fg='green', bold=True)
        click.echo("="*60)
        click.echo(f"  Title: {title}")
        if genre:
            click.echo(f"  Genre: {genre}")
        click.echo(f"  Lyrics: {len(prompt)} characters")
        click.echo(f"\n  Style Tags: {tags}")
        if negative_tags:
            click.echo(f"  Negative Tags: {negative_tags}")
        click.echo(f"\n  Instrumental: {'Yes (no vocals)' if instrumental else 'No (with vocals)'}")
        if style_weight is not None:
            click.echo(f"  Style Weight: {style_weight}")
        if weirdness is not None:
            click.echo(f"  Weirdness: {weirdness}")
        click.echo(f"  Model: {model}")
        click.echo("="*60)
        
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
                clip_id = clip.get('clip_id')
                if not clip_id:
                    click.secho("✗ Clip ID not found", fg='red')
                else:
                    click.secho(f"\nGetting WAV URL for clip {clip_id}...", fg='cyan')
                    wav_response = client.get_wav_url(clip_id)
                    
                    if wav_response.get('message') == 'success' and 'data' in wav_response:
                        wav_url = wav_response['data'].get('wav_url')
                        
                        if wav_url:
                            wav_filename = client.sanitize_filename(title) + ".wav"
                            client.download_file(wav_url, wav_filename)
                            click.secho(f"✓ Downloaded: {wav_filename}", fg='green')
                        else:
                            click.secho("✗ WAV URL not available yet", fg='yellow')
                    else:
                        click.secho(f"✗ Failed to get WAV URL: {wav_response.get('message')}", fg='red')
        
    except KeyboardInterrupt:
        click.echo("\n\nExiting...")
    except (TracksMartinClientError, LyricsGeneratorError) as e:
        click.secho(f"\n✗ Error: {e}", fg='red', err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
