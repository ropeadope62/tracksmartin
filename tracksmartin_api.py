"""
Project: TracksMartin - Hits on Demand.
Module: API Client tracksmartin_api.py
Author: Dave C. (ropeadope62)
https://github.com/ropeadope62
"""

import requests
import time
import os
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

class SunoAPIError(Exception):
    """Custom exception for Suno API errors"""
    pass

class TracksMartinClientError(Exception):
    """Custom exception for TracksMartin client errors"""
    pass


class TracksMartinClient:
    """
    Client for interacting with the Suno AI Music Generation API
    
    Attributes:
        api_key (str): Your Suno API key
        base_url (str): Base URL for the Suno API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Suno API client
        
        Args:
            api_key: Your Suno API key. If None, will try to load from 
                    SUNO_API_KEY environment variable
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("SUNO_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it directly or set "
                "SUNO_API_KEY environment variable."
            )
        
        self.base_url = "https://api.sunoapi.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Internal method to make API requests
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: JSON data for POST requests
            params: Query parameters for GET requests
            
        Returns:
            Response data as dictionary
            
        Raises:
            SunoAPIError: If the API request fails
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            # Try to get more details from the response
            error_msg = f"API request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f"\nResponse details: {error_detail}"
                except:
                    error_msg += f"\nResponse text: {e.response.text[:500]}"
            raise SunoAPIError(error_msg)
    
    
    def create_music(
        self,
        prompt: str,
        title: Optional[str] = None,
        tags: Optional[str] = None,
        style_weight: Optional[float] = None,
        weirdness_constraint: Optional[float] = None,
        negative_tags: Optional[str] = None,
        custom_mode: bool = True,
        make_instrumental: bool = False,
        mv: str = "chirp-v5",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create music with custom lyrics and style
        
        Args:
            prompt: Lyrics (when not instrumental) or description (when instrumental)
            title: Title of the song
            tags: Style tags (e.g., "future pop, energetic, 120 bpm, female vocals")
            style_weight: Weight for style adherence (0.0 to 1.0).
            weirdness_constraint: Constraint for weirdness/creativity (0.0 to 1.0). 
            negative_tags: Tags to avoid in generation
            custom_mode: Use custom mode (True) or random mode (False)
            make_instrumental: Generate instrumental only
            mv: Model version (chirp-v3-5, chirp-v4, chirp-v4-5, chirp-v5)
            
        Returns:
            Dictionary containing task_id for polling
        """
        
        # Prepare the base payload for the request
        payload = {
            "custom_mode": custom_mode,
            "make_instrumental": make_instrumental,
            "mv": mv
        }
        
        # For instrumental tracks, use prompt as gpt_description_prompt
        # For vocal tracks, use prompt as lyrics
        if make_instrumental:
            payload["gpt_description_prompt"] = prompt
        else:
            payload["prompt"] = prompt
        
        # Add optional parameters if provided
        if title:
            payload["title"] = title
        if tags:
            payload["tags"] = tags
        if style_weight is not None:
            payload["style_weight"] = style_weight
        if weirdness_constraint is not None:
            payload["weirdness_constraint"] = weirdness_constraint
        if negative_tags:
            payload["negative_tags"] = negative_tags
        
        # In case of future changes to the endpoint parameters, lets add them here so they can be used. 
        payload.update(kwargs)
        
        response = self._make_request("POST", "suno/create", data=payload)
        
        if "task_id" not in response:
            raise SunoAPIError(f"No task_id in response: {response}")
        
        return response
    
    def create_music_with_description(
        self,
        gpt_description_prompt: str,
        make_instrumental: bool = False,
        mv: str = "chirp-v5"
    ) -> Dict[str, Any]:
        """
        Create music from a description (no-custom mode)
        
        This request will generate music based on a description rather than specific tags. 
        
        Args:
            gpt_description_prompt: Description of the desired music (e.g., "happy song", 
                                   "energetic rock music with guitar solos")
            make_instrumental: Generate instrumental only (no vocals)
            mv: Model version (chirp-v3-5, chirp-v4, chirp-v4-5, chirp-v5)
            
        Returns:
            Dictionary containing task_id for polling
            
        Example:
            >>> api = SunoAPI()
            >>> result = api.create_music_with_description(
            ...     gpt_description_prompt="upbeat pop song about summer",
            ...     make_instrumental=False,
            ...     mv="chirp-v5"
            ... )
            >>> task_id = result['task_id']
        """
        payload = {
            "custom_mode": False,
            "gpt_description_prompt": gpt_description_prompt,
            "make_instrumental": make_instrumental,
            "mv": mv
        }
        
        response = self._make_request("POST", "suno/create", data=payload)
        
        if "task_id" not in response:
            raise SunoAPIError(f"No task_id in response: {response}")
        
        return response
    
    def extend_music(
        self,
        continue_clip_id: str,
        prompt: str = "",
        continue_at: int = 0,
        tags: Optional[str] = None,
        title: Optional[str] = None,
        custom_mode: bool = True,
        mv: str = "chirp-v5"
    ) -> Dict[str, Any]:
        """
        Extend an existing music clip
        
        Args:
            continue_clip_id: ID of the clip to extend
            prompt: Additional lyrics for the extension
            continue_at: Time in seconds where to continue from (default: 0 for end of song)
            tags: Style tags for the extension
            title: Title for the extended version
            custom_mode: Use custom mode (default: True)
            mv: Model version (default: chirp-v5)
            
        Returns:
            Dictionary containing task_id for polling
        """
        payload = {
            "task_type": "extend_music",
            "continue_clip_id": continue_clip_id,
            "continue_at": continue_at,
            "custom_mode": custom_mode,
            "mv": mv
        }
        
        if prompt:
            payload["prompt"] = prompt
        if tags:
            payload["tags"] = tags
        if title:
            payload["title"] = title
        
        return self._make_request("POST", "suno/create", data=payload)
    
    def concat_music(
        self,
        continue_clip_id: str
    ) -> Dict[str, Any]:
        """
        Concatenate/complete an extended music clip
        
        This gets the complete song after an extend operation.
        
        Args:
            continue_clip_id: ID of the extended clip to concatenate
            
        Returns:
            Dictionary containing task_id for polling
        """
        payload = {
            "task_type": "concat_music",
            "continue_clip_id": continue_clip_id
        }
        return self._make_request("POST", "suno/create", data=payload)
    
    def cover_music(
        self,
        continue_clip_id: str,
        prompt: Optional[str] = None,
        title: Optional[str] = None,
        tags: Optional[str] = None,
        custom_mode: bool = True,
        mv: str = "chirp-v5"
    ) -> Dict[str, Any]:
        """
        Create a cover version of existing music (Suno API)
        
        Args:
            continue_clip_id: ID of the clip to cover (required)
            prompt: New lyrics for the cover
            title: Title for the cover version
            tags: Style tags (e.g., "pop", "rock")
            custom_mode: Use custom mode (default: True)
            mv: Model version (default: chirp-v5)
            
        Returns:
            Dictionary containing task_id for polling
        """
        payload = {
            "task_type": "cover_music",
            "custom_mode": custom_mode,
            "continue_clip_id": continue_clip_id,
            "mv": mv
        }
        
        if prompt:
            payload["prompt"] = prompt
        if title:
            payload["title"] = title
        if tags:
            payload["tags"] = tags
        
        return self._make_request("POST", "suno/create", data=payload)
    
    def remaster(
        self,
        clip_id: str,
        variation_category: str = "normal",
        mv: str = "chirp-v5"
    ) -> Dict[str, Any]:
        """
        Remaster an existing clip to change the sonic interpretation
        
        Song must be generated with Suno first and clip_id supplied with the command, becoming the continue_clip_id. Best results with clips generated within 24 hours.
        
        Args:
            clip_id: ID of the clip to remaster (works best with clips < 24h old)
            variation_category: Intensity of changes:
                - "subtle": Minor changes
                - "normal": Moderate changes (default)
                - "high": Significant changes
            mv: Model version. Allowed: chirp-v4, chirp-v4-5-plus, chirp-v5
            
        Returns:
            Dictionary containing task_id for polling
            
        Raises:
            ValueError: If variation_category is invalid
            SunoAPIError: If the API request fails
        """
        valid_variations = ["subtle", "normal", "high"]
        if variation_category not in valid_variations:
            raise ValueError(
                f"variation_category must be one of {valid_variations}, "
                f"got '{variation_category}'"
            )
        
        valid_models = ["chirp-v4", "chirp-v4-5-plus", "chirp-v5"]
        if mv not in valid_models:
            raise ValueError(
                f"Model must be one of {valid_models} for remaster, "
                f"got '{mv}'"
            )
        
        payload = {
            "task_type": "remaster",
            "continue_clip_id": clip_id,
            "variation_category": variation_category,
            "mv": mv
        }
        
        return self._make_request("POST", "suno/create", data=payload)
    
    def add_vocal(
        self,
        clip_id: str,
        prompt: str,
        start_time: int,
        end_time: int,
        tags: Optional[str] = None,
        style_weight: float = 0.5,
        weirdness_constraint: float = 0.3,
        audio_weight: float = 0.7,
        vocal_gender: str = "f",
        mv: str = "chirp-v5"
    ) -> Dict[str, Any]:
        """
        Add vocals to uploaded music
        
        Add AI-generated vocals that match the original track to music
        uploaded via the API. Only works with tracks uploaded through the API
        and clip_id must be generated within 24 hours.
        
        Args:
            clip_id: ID of the uploaded clip (must be < 24h old)
            prompt: Lyrics for the vocals (use [Verse], [Chorus] tags)
            start_time: Start time in seconds for adding vocals
            end_time: End time in seconds for adding vocals
            tags: Style tags (e.g., "pop", "rock")
            style_weight: Weight of the style/tags (0.0 to 1.0, default: 0.5)
            weirdness_constraint: Randomness/creativity (0.0 to 1.0, default: 0.3)
            audio_weight: Weight of original audio (0.0 to 1.0, default: 0.7)
            vocal_gender: "f" for female, "m" for male (default: "f")
            mv: Model version (chirp-v4-5-plus or chirp-v5, default: chirp-v5)
            
        Returns:
            Dictionary containing task_id for polling
            
        Raises:
            ValueError: If parameters are invalid
            SunoAPIError: If the API request fails
        """
        # Validate vocal_gender
        if vocal_gender not in ["f", "m"]:
            raise ValueError(
                f"vocal_gender must be 'f' (female) or 'm' (male), "
                f"got '{vocal_gender}'"
            )
        
        # Validate model
        valid_models = ["chirp-v4-5-plus", "chirp-v5"]
        if mv not in valid_models:
            raise ValueError(
                f"Model must be one of {valid_models} for add_vocal, "
                f"got '{mv}'"
            )
        
        # Validate weight parameters
        for name, value in [("style_weight", style_weight),
                            ("weirdness_constraint", weirdness_constraint),
                            ("audio_weight", audio_weight)]:
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0.0 and 1.0")
        
        # Validate time parameters
        if start_time < 0:
            raise ValueError("start_time must be >= 0")
        if end_time <= start_time:
            raise ValueError("end_time must be greater than start_time")
        
        payload = {
            "task_type": "add_vocals",
            "continue_clip_id": clip_id,
            "mv": mv,
            "custom_mode": True,
            "prompt": prompt,
            "style_weight": style_weight,
            "weirdness_constraint": weirdness_constraint,
            "audio_weight": audio_weight,
            "overpainting_start_s": start_time,
            "overpainting_end_s": end_time,
            "vocal_gender": vocal_gender
        }
        
        if tags:
            payload["tags"] = tags
        
        return self._make_request("POST", "suno/create", data=payload)
    
    def stems_basic(self, clip_id: str) -> Dict[str, Any]:
        """
        Extract basic stems (vocals, instrumentals) from a clip
        
        Args:
            clip_id: ID of the clip to extract stems from
            
        Returns:
            Dictionary containing task_id for polling
        """
        payload = {"clip_id": clip_id}
        return self._make_request("POST", "suno/stems/basic", data=payload)
    
    def stems_full(self, clip_id: str) -> Dict[str, Any]:
        """
        Extract full stems (vocals, bass, drums, other) from a generated clip
        
        Args:
            clip_id: ID of the clip to extract stems from
            
        Returns:
            Dictionary containing task_id for polling
        """
        payload = {"clip_id": clip_id}
        return self._make_request("POST", "suno/stems/full", data=payload)
    
    def create_persona(
        self,
        clip_id: str,
        name: str
    ) -> Dict[str, Any]:
        """
        Create a vocal persona from a clip
        
        Extract the vocal characteristics from a song clip to create a reusable
        persona (virtual singer) that can be used in future songs.
        
        Args:
            clip_id: The clip ID to extract vocal persona from
            name: Name for the persona
            
        Returns:
            Dictionary containing persona_id and code
            
        """
        payload = {
            "clip_id": clip_id,
            "name": name
        }
        return self._make_request("POST", "suno/persona", data=payload)
    
    def create_music_with_persona(
        self,
        persona_id: str,
        prompt: str,
        title: Optional[str] = None,
        tags: Optional[str] = None,
        custom_mode: bool = True,
        mv: str = "chirp-v5"
    ) -> Dict[str, Any]:
        """
        Create music using a specific persona (virtual singer)
        
        Use a previously created persona to generate new music with the same
        vocal characteristics but different lyrics and style.
        
        Args:
            persona_id: ID of the persona to use
            prompt: Lyrics for the song
            title: Title of the song
            tags: Style tags (e.g., "pop, upbeat")
            custom_mode: Use custom mode (default: True)
            mv: Model version (default: chirp-v5)
            
        Returns:
            Dictionary containing task_id for polling
        """
        payload = {
            "task_type": "persona_music",
            "persona_id": persona_id,
            "prompt": prompt,
            "custom_mode": custom_mode,
            "mv": mv
        }
        
        if title:
            payload["title"] = title
        if tags:
            payload["tags"] = tags
        
        return self._make_request("POST", "suno/create", data=payload)
    
    # ==================== QUERYING SUNO ====================
    
    def get_music(self, task_id: str) -> Dict[str, Any]:
        """
        Get music generation status and details by task_id
        
        Args:
            task_id: The task ID returned from create_music or other operations
            
        Returns:
            Dictionary containing music details and status
        """
        return self._make_request("GET", f"suno/task/{task_id}")
    
    def get_midi(self, clip_id: str, max_attempts: int = 20, interval: int = 10) -> Dict[str, Any]:
        """
        Get MIDI format URL for a clip (with polling)
        
        This endpoint requires polling as MIDI generation is asynchronous.
        Will retry until MIDI is ready or max_attempts is reached.
        
        Args:
            clip_id: The clip ID
            max_attempts: Maximum number of polling attempts (default: 20)
            interval: Seconds between polling attempts (default: 10)
        Returns:
            Dictionary containing midi_url and instruments data
        """
        payload = {"clip_id": clip_id}
        
        for attempt in range(max_attempts):
            response = self._make_request("POST", "suno/midi", data=payload)
            
            # Check if successful
            if response.get('code') == 200 and 'data' in response:
                data = response['data']
                # Check if midi_url is present (not just "generating midi...")
                if data.get('midi_url') and not data.get('midi_url').startswith('Failed'):
                    return response
            
            # If still generating, wait and retry
            if attempt < max_attempts - 1:
                time.sleep(interval)
        
        # Return last response if max attempts reached
        return response
    
    def get_wav_url(self, clip_id: str) -> Dict[str, Any]:
        """
        Get WAV format URL for a clip
        
        Args:
            clip_id: The clip ID
            
        Returns:
            Dictionary containing wav_url
        """
        payload = {"clip_id": clip_id}
        return self._make_request("POST", "suno/wav", data=payload)
    
    def upload_music(self, url: str) -> Dict[str, Any]:
        """
        Upload local music from a URL and get a clip_id for use in other ops
        
        Args:
            url: Public URL to the audio file to upload
            
        Returns:
            Dictionary containing clip_id of the uploaded music
        """
        payload = {"url": url}
        return self._make_request("POST", "suno/upload", data=payload)
    
    def get_credits(self) -> Dict[str, Any]:
        """
        Get remaining API credits
        
        Returns:
            Dictionary containing credit information
        """
        return self._make_request("GET", "get-credits")
    
    # ==================== HELPER METHODS ====================
    
    def poll_until_complete(
        self,
        task_id: str,
        max_attempts: int = 20,
        interval: int = 15,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Poll a task until it's complete or fails
        
        Args:
            task_id: The task ID to poll
            max_attempts: Maximum number of polling attempts
            interval: Seconds between polling attempts
            verbose: Print status updates
            
        Returns:
            Dictionary containing completed music details
            
        Raises:
            SunoAPIError: If polling times out or generation fails
        """
        for attempt in range(1, max_attempts + 1):
            time.sleep(interval)
            
            response = self.get_music(task_id)
            
            # Handle "not ready" response
            if response.get('type') == 'not_ready':
                if verbose:
                    print(f"Attempt {attempt}/{max_attempts}: Task not ready yet...")
                continue
            
            # Handle normal response format
            if response.get('code') != 200 or 'data' not in response:
                if verbose:
                    print(f"Attempt {attempt}/{max_attempts}: Waiting for data...")
                continue
            
            clips = response['data']
            
            if not clips:
                if verbose:
                    print(f"Attempt {attempt}/{max_attempts}: No clips yet...")
                continue
            
            clip = clips[0]
            state = clip.get('state')
            
            if state == "succeeded":
                if verbose:
                    print(f"\nGeneration complete! (Task ID: {task_id})")
                return clip
            
            elif state in ["error", "failed"]:
                raise SunoAPIError(
                    f"Generation failed with state: {state}"
                )
            
            if verbose:
                print(f"Attempt {attempt}/{max_attempts}: {state}...")
        
        raise SunoAPIError(
            f"Polling timed out after {max_attempts * interval} seconds"
        )
    
    def download_file(
        self,
        url: str,
        output_path: str,
        chunk_size: int = 8192
    ) -> None:
        """
        Download a file from a URL
        
        Args:
            url: URL to download from
            output_path: Path where to save the file
            chunk_size: Size of chunks to download
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    
        except requests.exceptions.RequestException as e:
            raise SunoAPIError(f"Download failed: {str(e)}")
    
    @staticmethod
    def sanitize_filename(name: str) -> str:
        """
        Create a safe filename from a string
        
        Args:
            name: Original filename/title
            
        Returns:
            Sanitized filename
        """
        return "".join(
            c for c in name if c.isalnum() or c in (' ', '_', '-')
        ).strip()
