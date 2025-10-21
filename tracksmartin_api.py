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
            prompt: Lyrics or description for the song
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
            "prompt": prompt,
            "make_instrumental": make_instrumental,
            "mv": mv
        }
        
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
        clip_id: str,
        prompt: str = "",
        continue_at: int = 0,
        tags: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extend an existing music clip
        
        Args:
            clip_id: ID of the clip to extend
            prompt: Additional lyrics for the extension
            continue_at: Time in seconds where to continue from
            tags: Style tags
            title: Title for the extended version
            
        Returns:
            Dictionary containing task_id for polling
        """
        payload = {
            "clip_id": clip_id,
            "prompt": prompt,
            "continue_at": continue_at
        }
        
        if tags:
            payload["tags"] = tags
        if title:
            payload["title"] = title
        
        return self._make_request("POST", "suno/extend", data=payload)
    
    def concat_music(
        self,
        clip_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Concatenate multiple music clips
        
        Args:
            clip_ids: List of clip IDs to concatenate
            
        Returns:
            Dictionary containing task_id for polling
        """
        payload = {"clip_ids": clip_ids}
        return self._make_request("POST", "suno/concat", data=payload)
    
    def cover_music(
        self,
        clip_id: str,
        new_prompt: Optional[str] = None,
        new_tags: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a cover version of existing music
        
        Args:
            clip_id: ID of the clip to cover
            new_prompt: New lyrics for the cover
            new_tags: New style tags
            
        Returns:
            Dictionary containing task_id for polling
        """
        payload = {"clip_id": clip_id}
        
        if new_prompt:
            payload["prompt"] = new_prompt
        if new_tags:
            payload["tags"] = new_tags
        
        return self._make_request("POST", "suno/cover", data=payload)
    
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
        name: str,
        description: str,
        sample_clip_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Create a vocal persona from sample clips
        
        Args:
            name: Name for the persona
            description: Description of the persona
            sample_clip_ids: List of clip IDs to use as samples
            
        Returns:
            Dictionary containing persona_id
        """
        payload = {
            "name": name,
            "description": description,
            "sample_clip_ids": sample_clip_ids
        }
        return self._make_request("POST", "suno/persona", data=payload)
    
    def create_music_with_persona(
        self,
        persona_id: str,
        prompt: str,
        title: Optional[str] = None,
        tags: Optional[str] = None,
        mv: str = "chirp-v5"
    ) -> Dict[str, Any]:
        """
        Create music using a specific persona
        
        Args:
            persona_id: ID of the persona to use
            prompt: Lyrics for the song
            title: Title of the song
            tags: Style tags
            mv: Model version
            
        Returns:
            Dictionary containing task_id for polling
        """
        payload = {
            "persona_id": persona_id,
            "prompt": prompt,
            "mv": mv
        }
        
        if title:
            payload["title"] = title
        if tags:
            payload["tags"] = tags
        
        return self._make_request("POST", "suno/persona/music", data=payload)
    
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
    
    def get_credits(self) -> Dict[str, Any]:
        """
        Get remaining API credits
        
        Returns:
            Dictionary containing credit information
        """
        return self._make_request("GET", "get-credits")
    
    # ==================== UPLOAD ====================
    #todo: Implement upload_music method
    def upload_music(
        self,
        file_path: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload an audio file to Suno
        
        Args:
            file_path: Path to the audio file
            title: Title for the uploaded file
            
        Returns:
            Dictionary containing upload details and clip_id
        """
    
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
