import os
import sys
import json
import argparse
import subprocess
import re
from datetime import datetime
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables from .env file
load_dotenv()

def check_env_vars():
    """Checks if all required environment variables are set."""
    required_vars = ["SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET", "SPOTIPY_REDIRECT_URI"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print("Error: Missing environment variables in .env file.")
        print("Please copy .env.template to .env and fill in the following values:")
        for var in missing:
            print(f"  - {var}")
        print("\nYou can get these credentials by creating an app on the Spotify Developer Dashboard:")
        print("https://developer.spotify.com/dashboard")
        sys.exit(1)

def get_spotify_client():
    """Authenticates with Spotify and returns a Spotify client instance."""
    check_env_vars()
    
    # Scopes needed for reading and writing playlists
    scopes = [
        "playlist-read-private",
        "playlist-read-collaborative",
        "playlist-modify-public",
        "playlist-modify-private"
    ]
    
    # SpotifyOAuth handles retrieving token, caching, and refreshing automatically
    auth_manager = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=" ".join(scopes),
        open_browser=True
    )
    
    return spotipy.Spotify(auth_manager=auth_manager)

def get_playlist_tracks(sp, playlist_id):
    """Fetches all tracks from a playlist, handling API pagination."""
    tracks_info = []
    
    # We query the newer 'playlists/{playlist_id}/items' endpoint directly
    # to avoid 403 errors with older versions of spotipy (like the one in NixOS)
    # which still target the deprecated '/tracks' endpoint.
    # Note: The modern endpoint nests the track details under the 'item' key rather than 'track'.
    results = sp._get(
        f"playlists/{playlist_id}/items",
        fields="items(item(id,name,artists(id,name),album(id,name,release_date),duration_ms,popularity,uri,is_local)),next",
        additional_types="track",
        limit=100
    )
    
    while results:
        for item in results.get('items', []):
            track = item.get('item')
            if not track:
                continue
            
            # Skip local tracks since they might not have IDs/URIs for Spotify API actions
            if track.get('is_local'):
                continue
                
            artists = [artist['name'] for artist in track.get('artists', [])]
            
            tracks_info.append({
                'id': track.get('id'),
                'name': track.get('name'),
                'artists': artists,
                'album': track.get('album', {}).get('name'),
                'release_date': track.get('album', {}).get('release_date'),
                'duration_ms': track.get('duration_ms'),
                'popularity': track.get('popularity'),
                'uri': track.get('uri')
            })
            
        # Get next page if it exists
        if results.get('next'):
            results = sp.next(results)
        else:
            results = None
            
    return tracks_info

def extract_playlist_id(playlist_input):
    """Extracts playlist ID from a URL, URI, or uses the string as-is."""
    if "spotify.com/playlist/" in playlist_input:
        # Split by slash and strip query parameters
        parts = playlist_input.split("playlist/")
        if len(parts) > 1:
            return parts[1].split("?")[0]
    elif playlist_input.startswith("spotify:playlist:"):
        return playlist_input.split("spotify:playlist:")[1]
    
    return playlist_input.strip()

def extract_json_content(text):
    """Extracts raw JSON content from a text string that might contain markdown blocks or surrounding text."""
    if not text:
        return None
    text = text.strip()
    
    # Strip markdown block wrappers if present (e.g. ```json ... ``` or ``` ...)
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline:].strip()
        if text.endswith("```"):
            text = text[:-3].strip()
            
    # Find the outermost braces to clean up any extra text
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1:
        text = text[first_brace:last_brace+1]
        
    return text

STATES_DIR = "states"

def update_description_timestamp(description):
    """Strips any existing ' (Last sorted: ...)' tag and appends a new one with the current timestamp."""
    if not description:
        description = "[ai sorted]"
    clean_desc = re.sub(r"\s*\(Last sorted: \d{4}-\d{2}-\d{2} \d{2}:\d{2}\)", "", description.strip(), flags=re.IGNORECASE)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"{clean_desc} (Last sorted: {now_str})".lower()

def add_playlist_items(sp, playlist_id, uris, position=None):
    """Adds tracks to a playlist using the modern '/items' endpoint to avoid 403 errors."""
    plid = sp._get_id("playlist", playlist_id)
    payload = {"uris": uris}
    if position is not None:
        payload["position"] = position
    return sp._post(f"playlists/{plid}/items", payload=payload)

def remove_playlist_items(sp, playlist_id, uris, snapshot_id=None):
    """Removes tracks from a playlist using the modern '/items' endpoint to avoid 403 errors."""
    plid = sp._get_id("playlist", playlist_id)
    payload = {"items": [{"uri": uri} for uri in uris]}
    if snapshot_id:
        payload["snapshot_id"] = snapshot_id
    return sp._delete(f"playlists/{plid}/items", payload=payload)

def replace_playlist_tracks(sp, playlist_id, track_ids):
    """Replaces all tracks in a Spotify playlist using the modern '/items' endpoint."""
    plid = sp._get_id("playlist", playlist_id)
    uris = [f"spotify:track:{tid}" for tid in track_ids]
    
    # Replace first chunk of 100 (or clear if empty)
    first_chunk = uris[:100]
    payload = {"uris": first_chunk}
    sp._put(f"playlists/{plid}/items", payload=payload)
    
    # Add remaining tracks in chunks of 100
    for i in range(100, len(uris), 100):
        chunk = uris[i:i+100]
        add_playlist_items(sp, plid, chunk)

def load_sorting_state(input_playlist_id):
    """Loads the sorted state for the given playlist ID if it exists."""
    if not input_playlist_id:
        return None
    filename = os.path.join(STATES_DIR, f"sorting_state_{input_playlist_id}.json")
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load sorting state file: {e}")
    return None

def save_sorting_state(input_playlist_id, input_playlist_name, created_playlists):
    """Saves the sorted state for the given playlist ID."""
    if not input_playlist_id:
        return
    
    # Ensure states directory exists
    os.makedirs(STATES_DIR, exist_ok=True)
    
    filename = os.path.join(STATES_DIR, f"sorting_state_{input_playlist_id}.json")
    state = {
        "input_playlist_id": input_playlist_id,
        "input_playlist_name": input_playlist_name,
        "created_playlists": created_playlists
    }
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"Saved sorting state to: {filename}")
    except Exception as e:
        print(f"Failed to save sorting state: {e}")

def query_ai_for_sorting(tracks, query_instruction=None, existing_playlists=None):
    """Invokes the Antigravity CLI to categorize tracks based on user query instructions."""
    # Construct a compact track list for the prompt to conserve context space
    tracks_str = ""
    for i, t in enumerate(tracks):
        artists = ", ".join(t['artists'])
        tracks_str += f"{i}. {t['name']} - {artists} (ID: {t['id']})\n"
        
    if existing_playlists:
        existing_categories_str = "\n".join([
            f"- {pl['name']}: {pl['description']}" for pl in existing_playlists
        ])
        prompt = (
            f"You are helping to sort new songs into an existing set of playlist categories.\n\n"
            f"Existing Playlist Categories:\n{existing_categories_str}\n\n"
            f"Instructions:\n"
            f"1. Group the new tracks listed below into these existing categories where they fit best.\n"
            f"2. If a track absolutely does not fit any of the existing categories, you may propose a new category. The name of any new category must be strictly 1 or 2 words, in all lowercase with a dash (e.g. 'ambient-chill', 'hard-rock'). The description of any new category must start with '[ai sorted]'.\n"
            f"3. Do NOT include any emojis in the playlist names."
        )
    else:
        prompt = (
            f"Analyze the following Spotify tracks and group them into logical, cohesive playlist categories based on their genre, vibe, mood, or style.\n\n"
            f"Strict Constraints on Playlist Format:\n"
            f"1. Playlist 'name' must be very short—strictly 1 or 2 words, in all lowercase with a dash between words (e.g. 'chill-pop', 'classic-rock', 'acoustic'). Do NOT include any emojis.\n"
            f"2. Use the 'description' field to hold a longer descriptive title/theme (e.g. 'Mellow Synth-Pop and 80s Dance Pop') followed by details explaining the mood/style. Start the description with the tag '[ai sorted]'."
        )
        
    if query_instruction:
        prompt += f"\n\nAdditional user sorting instructions: {query_instruction}"
    
    prompt += (
        f"\n\nYour response must be a valid JSON object matching this structure (do not include markdown backticks like ```json, do not write explanations, return ONLY the raw JSON):\n"
        f"{{\n"
        f"  \"playlists\": [\n"
        f"    {{\n"
        f"      \"name\": \"chill-pop\",\n"
        f"      \"description\": \"[ai sorted] Mellow Synth-Pop and 80s Dance Pop. Cozy, late-night listening vibe.\",\n"
        f"      \"track_ids\": [\"track_id_1\", \"track_id_2\"]\n"
        f"    }}\n"
        f"  ]\n"
        f"}}\n\n"
        f"Note: Ensure the 'track_ids' array contains the actual track IDs (e.g. from the list below, NOT the index numbers like 0, 1, 2).\n\n"
        f"Tracks to sort:\n{tracks_str}"
    )
    
    print("\nQuerying Antigravity CLI (agy) for sorting recommendations. Please wait...")
    try:
        result = subprocess.run(
            ["agy", "-p", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"\nError running agy CLI: {e.stderr}")
        return None
    except FileNotFoundError:
        print("\nError: 'agy' CLI command not found in your PATH.")
        print("Please make sure the Antigravity CLI is installed and available.")
        return None

def parse_proposed_playlists(raw_ai_output, tracks):
    """Parses the JSON AI output and resolves track ID/index mappings back to original tracks."""
    raw_json = extract_json_content(raw_ai_output)
    if not raw_json:
        print("Error: Could not find JSON block in AI response.")
        return None
        
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse response as JSON: {e}")
        print(f"Cleaned output was:\n{raw_json}")
        return None
        
    playlists = data.get("playlists", [])
    if not playlists:
        print("Error: No playlists found in AI response.")
        return None
        
    # Build maps for robust resolution of tracks
    id_map = {t['id']: t for t in tracks if t.get('id')}
    index_map = {str(i): t for i, t in enumerate(tracks)}
    
    proposed_playlists = []
    for pl in playlists:
        name = pl.get("name")
        if name:
            # Enforce lowercase and dash separation
            name = name.strip().lower().replace(" ", "-")
            
        description = pl.get("description", "")
        track_ids = pl.get("track_ids", [])
        
        # Ensure description starts with '[ai sorted]' and is completely lowercase
        desc_stripped = description.strip().lower()
        if desc_stripped and not desc_stripped.startswith("[ai sorted]"):
            description = f"[ai sorted] {desc_stripped}"
        elif not desc_stripped:
            description = "[ai sorted]"
        else:
            description = desc_stripped
            
        pl_tracks = []
        for tid in track_ids:
            tid_str = str(tid).strip()
            # 1. Resolve by direct ID
            if tid_str in id_map:
                pl_tracks.append(id_map[tid_str])
            # 2. Resolve by index reference
            elif tid_str in index_map:
                pl_tracks.append(index_map[tid_str])
            # 3. Resolve by partial matching (in case AI trimmed it)
            else:
                found = False
                for track_id, track_obj in id_map.items():
                    if tid_str in track_id or track_id in tid_str:
                        pl_tracks.append(track_obj)
                        found = True
                        break
                if not found:
                    print(f"Warning: Could not find track corresponding to ID reference '{tid}'")
                    
        if pl_tracks:
            proposed_playlists.append({
                "name": name,
                "description": description,
                "tracks": pl_tracks
            })
            
    return proposed_playlists

def display_proposed_playlists(proposed_playlists):
    """Displays the grouped playlists and their tracks to the user."""
    print("\n" + "="*50)
    print("           PROPOSED SUBSET PLAYLISTS")
    print("="*50)
    for idx, pl in enumerate(proposed_playlists, 1):
        print(f"\n{idx}. 🎵 {pl['name']}")
        if pl['description']:
            print(f"   Description: {pl['description']}")
        print(f"   Tracks ({len(pl['tracks'])}):")
        for track in pl['tracks'][:5]:
            artists = ", ".join(track['artists'])
            print(f"     - {track['name']} - {artists}")
        if len(pl['tracks']) > 5:
            print(f"     - ... and {len(pl['tracks']) - 5} more")
    print("="*50)

def create_spotify_playlists(sp, proposed_playlists):
    """Creates the proposed playlists on Spotify, populates them, and returns state metadata."""
    try:
        user_id = sp.current_user()['id']
    except Exception as e:
        print(f"Failed to get current user details: {e}")
        return []
        
    created_playlists_state = []
    print(f"\nCreating playlists on Spotify account: {user_id}")
    for pl in proposed_playlists:
        name = pl['name']
        description = update_description_timestamp(pl['description'])
        tracks = pl['tracks']
        
        print(f"\nCreating playlist '{name}' ({len(tracks)} tracks)...")
        try:
            # We call the modern 'me/playlists' endpoint directly
            # to avoid 403 errors with older versions of spotipy (like the one in NixOS)
            # which still target the deprecated 'users/{user_id}/playlists' endpoint.
            playlist_data = {
                "name": name,
                "public": False,
                "collaborative": False,
                "description": description
            }
            new_pl = sp._post("me/playlists", payload=playlist_data)
            
            # Batch tracks in chunks of 100 for API safety
            track_uris = [t['uri'] for t in tracks if t.get('uri')]
            for i in range(0, len(track_uris), 100):
                chunk = track_uris[i:i+100]
                add_playlist_items(sp, new_pl['id'], chunk)
                
            print(f"Successfully created: {new_pl['external_urls']['spotify']}")
            
            created_playlists_state.append({
                "name": name,
                "id": new_pl['id'],
                "description": description,
                "track_ids": [t['id'] for t in tracks if t.get('id')]
            })
        except Exception as e:
            print(f"Failed to create playlist '{name}': {e}")
            
    return created_playlists_state

def main():
    parser = argparse.ArgumentParser(description="Read, capture, and sort a Spotify playlist into subset playlists.")
    parser.add_argument(
        "playlist", 
        nargs="?", 
        help="The Spotify Playlist URL, URI, or ID (e.g. spotify:playlist:37i9dQZF1DXcBWIGmq5BmE)"
    )
    parser.add_argument(
        "--output", 
        default="playlist_tracks.json", 
        help="Output JSON file path (default: playlist_tracks.json)"
    )
    parser.add_argument(
        "--sort",
        action="store_true",
        help="Trigger the AI sorting process"
    )
    parser.add_argument(
        "--query",
        help="Provide specific instructions for AI sorting (e.g., 'group by decade', 'acoustic vs electronic'). Use 'force' to reset existing sort state."
    )
    args = parser.parse_args()
    
    tracks = []
    playlist_name = "Cached Playlist"
    playlist_id = None
    
    # Check if we should load cached tracks or fetch fresh ones
    use_cache = False
    if not args.playlist and os.path.exists(args.output):
        print(f"No playlist provided, but found cached tracks in: {args.output}")
        choice = input("Would you like to load from this cache file? (y/n): ").strip().lower()
        if choice == 'y':
            use_cache = True
            
    if use_cache:
        try:
            with open(args.output, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                tracks = cache_data.get("tracks", [])
                playlist_name = cache_data.get("playlist_name", "Cached Playlist")
                playlist_id = cache_data.get("playlist_id")
            print(f"Loaded {len(tracks)} tracks from cache: '{playlist_name}' (ID: {playlist_id})")
        except Exception as e:
            print(f"Failed to read cache file: {e}")
            use_cache = False
            
    if not use_cache:
        # Prompt for playlist if not provided via command line
        playlist_input = args.playlist
        if not playlist_input:
            playlist_input = input("Enter Spotify Playlist URL, URI, or ID: ").strip()
            if not playlist_input:
                print("Error: No playlist provided.")
                sys.exit(1)
                
        playlist_id = extract_playlist_id(playlist_input)
        
        print("Authenticating with Spotify...")
        try:
            sp = get_spotify_client()
            user = sp.current_user()
            print(f"Authenticated as: {user['display_name']} ({user['id']})")
        except Exception as e:
            print(f"Authentication failed: {e}")
            sys.exit(1)
            
        print(f"Fetching playlist details for ID: {playlist_id}...")
        try:
            playlist = sp.playlist(playlist_id, fields="name,description,owner(display_name)")
            playlist_name = playlist['name']
            print(f"\nPlaylist Name: {playlist_name}")
            print(f"Description: {playlist['description'] or 'No description'}")
            print(f"Owner: {playlist['owner']['display_name']}")
        except Exception as e:
            print(f"Failed to fetch playlist metadata: {e}")
            sys.exit(1)
            
        print("Retrieving tracks...")
        try:
            tracks = get_playlist_tracks(sp, playlist_id)
            print(f"Successfully retrieved {len(tracks)} tracks.")
        except Exception as e:
            print(f"Failed to retrieve tracks: {e}")
            sys.exit(1)
            
        # Save tracks list to JSON cache
        try:
            output_data = {
                "playlist_name": playlist_name,
                "playlist_id": playlist_id,
                "owner": playlist["owner"]["display_name"],
                "total_tracks": len(tracks),
                "tracks": tracks
            }
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"Saved track details to: {args.output}")
        except Exception as e:
            print(f"Failed to save output cache: {e}")

    # Load existing sorting state
    state = load_sorting_state(playlist_id)
    force_resort = args.query == "force"
    
    if state and not force_resort:
        print(f"\nFound existing sorting state for this playlist ('{state['input_playlist_name']}')")
        
        # Check if target playlists on Spotify are in sync with state
        out_of_sync = False
        spotify_playlists_tracks = {}
        
        print("\nVerifying synchronization of target playlists on Spotify...")
        if 'sp' not in locals():
            sp = get_spotify_client()
            
        state_playlists = state.get("created_playlists", [])
        for spl in state_playlists:
            try:
                actual_tracks = get_playlist_tracks(sp, spl['id'])
                actual_ids = [t['id'] for t in actual_tracks if t.get('id')]
                spotify_playlists_tracks[spl['id']] = actual_ids
                
                state_ids = spl.get("track_ids", [])
                if set(actual_ids) != set(state_ids):
                    print(f"⚠️ Playlist '{spl['name']}' is out of sync with stored state.")
                    print(f"  - In State:   {len(state_ids)} tracks")
                    print(f"  - On Spotify: {len(actual_ids)} tracks")
                    out_of_sync = True
            except Exception as e:
                print(f"Warning: Could not verify sync state of playlist '{spl['name']}': {e}")
                
        if out_of_sync:
            print("\nSpotify playlists do not match your stored state.")
            print("Options:")
            print("  1. Revert Spotify playlists to match the stored state.")
            print("  2. Update the stored state to match the current Spotify playlists.")
            sync_choice = input("Select an option (1 or 2): ").strip()
            
            if sync_choice == '1':
                print("\nReverting Spotify playlists to match stored state...")
                for spl in state_playlists:
                    actual_ids = spotify_playlists_tracks.get(spl['id'], [])
                    state_ids = spl.get("track_ids", [])
                    if set(actual_ids) != set(state_ids):
                        print(f"  Updating '{spl['name']}' tracks on Spotify...")
                        replace_playlist_tracks(sp, spl['id'], state_ids)
                        new_desc = update_description_timestamp(spl.get('description', ''))
                        try:
                            sp.playlist_change_details(spl['id'], description=new_desc)
                            spl['description'] = new_desc
                        except Exception as e:
                            print(f"Failed to update description for '{spl['name']}': {e}")
                save_sorting_state(playlist_id, playlist_name, state_playlists)
                print("Reversion complete. Spotify playlists match stored state.")
            elif sync_choice == '2':
                print("\nUpdating stored state to match current Spotify playlists...")
                for spl in state_playlists:
                    actual_ids = spotify_playlists_tracks.get(spl['id'], [])
                    spl['track_ids'] = actual_ids
                    new_desc = update_description_timestamp(spl.get('description', ''))
                    try:
                        sp.playlist_change_details(spl['id'], description=new_desc)
                        spl['description'] = new_desc
                    except Exception as e:
                        print(f"Failed to update description for '{spl['name']}': {e}")
                save_sorting_state(playlist_id, playlist_name, state_playlists)
                print("State updated successfully.")
            else:
                print("Invalid choice. Exiting.")
                sys.exit(1)
                
        # Build set of IDs in current playlist vs state
        current_ids = {t['id'] for t in tracks if t.get('id')}
        state_playlists = state.get("created_playlists", [])
        
        state_ids = set()
        for spl in state_playlists:
            state_ids.update(spl.get("track_ids", []))
            
        new_track_objs = [t for t in tracks if t.get('id') and t['id'] not in state_ids]
        removed_ids = state_ids - current_ids
        
        print("\nStatus vs Sorted State:")
        print(f"  - Total tracks currently in playlist: {len(tracks)}")
        print(f"  - Tracks already sorted in state:    {len(state_ids)}")
        print(f"  - New tracks to sort:                {len(new_track_objs)}")
        print(f"  - Removed tracks to clean up:        {len(removed_ids)}")
        
        if not new_track_objs and not removed_ids:
            print("\nAll tracks are up to date and correctly sorted.")
            choice = input("Would you like to force a complete re-sort? (y/n): ").strip().lower()
            if choice == 'y':
                state = None
            else:
                print("Exiting.")
                sys.exit(0)
                
        if state:
            # 1. Handle removed tracks
            if removed_ids:
                print(f"\nDetected {len(removed_ids)} tracks removed from the input playlist.")
                confirm_remove = input("Would you like to remove these tracks from the sorted playlists on Spotify? (y/n): ").strip().lower()
                if confirm_remove == 'y':
                    if 'sp' not in locals():
                        print("Authenticating with Spotify for removal permissions...")
                        sp = get_spotify_client()
                    
                    for spl in state_playlists:
                        pl_removed_ids = [tid for tid in spl.get("track_ids", []) if tid in removed_ids]
                        if pl_removed_ids:
                            print(f"Removing {len(pl_removed_ids)} tracks from '{spl['name']}'...")
                            try:
                                uris_to_remove = [f"spotify:track:{tid}" for tid in pl_removed_ids]
                                for i in range(0, len(uris_to_remove), 100):
                                    chunk = uris_to_remove[i:i+100]
                                    remove_playlist_items(sp, spl['id'], chunk)
                                spl['track_ids'] = [tid for tid in spl['track_ids'] if tid not in pl_removed_ids]
                                
                                # Update timestamp description since items changed
                                new_desc = update_description_timestamp(spl.get('description', ''))
                                sp.playlist_change_details(spl['id'], description=new_desc)
                                spl['description'] = new_desc
                            except Exception as e:
                                print(f"Failed to remove tracks from '{spl['name']}': {e}")
                                
                    save_sorting_state(playlist_id, playlist_name, state_playlists)
                    
            # 2. Handle new tracks
            if new_track_objs:
                print(f"\nFound {len(new_track_objs)} new tracks to sort:")
                for i, t in enumerate(new_track_objs[:10], 1):
                    artists_str = ", ".join(t['artists'])
                    print(f"  {i}. {t['name']} - {artists_str}")
                if len(new_track_objs) > 10:
                    print(f"  ... and {len(new_track_objs) - 10} more.")
                    
                choice = input("\nWould you like to sort these new tracks now? (y/n): ").strip().lower()
                if choice == 'y':
                    query_instruction = args.query
                    if query_instruction is None:
                        query_instruction = input(
                            "Enter sorting instructions for new tracks (or press Enter to let AI decide): "
                        ).strip()
                        if not query_instruction:
                            query_instruction = None
                            
                    # Query agy with existing playlists passed as reference
                    raw_ai_output = query_ai_for_sorting(new_track_objs, query_instruction, state_playlists)
                    if not raw_ai_output:
                        print("Sorting failed.")
                        sys.exit(1)
                        
                    proposed_new = parse_proposed_playlists(raw_ai_output, new_track_objs)
                    if not proposed_new:
                        print("Sorting failed: Could not parse AI response.")
                        sys.exit(1)
                        
                    display_proposed_playlists(proposed_new)
                    
                    confirm = input("\nApply these changes to your Spotify playlists? (y/n): ").strip().lower()
                    if confirm == 'y':
                        if 'sp' not in locals():
                            print("Authenticating with Spotify for creation/addition permissions...")
                            sp = get_spotify_client()
                            
                        existing_name_to_pl = {spl['name']: spl for spl in state_playlists}
                        
                        for pl in proposed_new:
                            name = pl['name']
                            description = pl['description']
                            pl_tracks = pl['tracks']
                            track_ids = [t['id'] for t in pl_tracks if t.get('id')]
                            track_uris = [t['uri'] for t in pl_tracks if t.get('uri')]
                            
                            if name in existing_name_to_pl:
                                target_pl = existing_name_to_pl[name]
                                print(f"\nAdding {len(pl_tracks)} new tracks to existing playlist '{name}'...")
                                try:
                                    for i in range(0, len(track_uris), 100):
                                        chunk = track_uris[i:i+100]
                                        add_playlist_items(sp, target_pl['id'], chunk)
                                    target_pl['track_ids'].extend(track_ids)
                                    
                                    # Update description timestamp on Spotify and in state
                                    new_desc = update_description_timestamp(target_pl.get('description', ''))
                                    sp.playlist_change_details(target_pl['id'], description=new_desc)
                                    target_pl['description'] = new_desc
                                    
                                    print("Added successfully.")
                                except Exception as e:
                                    print(f"Failed to add tracks: {e}")
                            else:
                                print(f"\nCreating new playlist '{name}' ({len(pl_tracks)} tracks)...")
                                try:
                                    new_desc = update_description_timestamp(description)
                                    playlist_data = {
                                        "name": name,
                                        "public": False,
                                        "collaborative": False,
                                        "description": new_desc
                                    }
                                    new_pl = sp._post("me/playlists", payload=playlist_data)
                                    for i in range(0, len(track_uris), 100):
                                        chunk = track_uris[i:i+100]
                                        add_playlist_items(sp, new_pl['id'], chunk)
                                    print(f"Successfully created: {new_pl['external_urls']['spotify']}")
                                    
                                    state_playlists.append({
                                        "name": name,
                                        "id": new_pl['id'],
                                        "description": new_desc,
                                        "track_ids": track_ids
                                    })
                                except Exception as e:
                                    print(f"Failed to create playlist: {e}")
                                    
                        save_sorting_state(playlist_id, playlist_name, state_playlists)
                        print("\nIncremental sorting completed successfully!")
                    else:
                        print("\nCancelled.")
            else:
                print("\nNo new tracks to sort.")
            sys.exit(0)
            
    # Determine if we should perform AI sorting (first time or force resort)
    should_sort = args.sort or (args.query is not None)
    if not should_sort:
        choice = input("\nWould you like to sort this playlist into subset playlists? (y/n): ").strip().lower()
        if choice == 'y':
            should_sort = True
            
    if should_sort:
        # Prompt for query instruction if not provided
        query_instruction = args.query
        if query_instruction is None or query_instruction == "force":
            query_instruction = input(
                "Enter sorting instructions (e.g. 'by decade', 'energetic/chill', or press Enter to let AI decide): "
            ).strip()
            if not query_instruction:
                query_instruction = None
                
        # Query the Antigravity CLI for grouping proposal
        raw_ai_output = query_ai_for_sorting(tracks, query_instruction)
        if not raw_ai_output:
            print("Sorting failed: Could not get a response from Antigravity.")
            sys.exit(1)
            
        # Parse output
        proposed_playlists = parse_proposed_playlists(raw_ai_output, tracks)
        if not proposed_playlists:
            print("Sorting failed: Could not parse playlists from AI response.")
            sys.exit(1)
            
        # Show results to the user
        display_proposed_playlists(proposed_playlists)
        
        # Confirm and create
        confirm = input("\nDo you want to create these playlists on your Spotify account? (y/n): ").strip().lower()
        if confirm == 'y':
            # Re-authenticate if we loaded from cache and don't have a spotipy client active yet
            if 'sp' not in locals():
                print("Authenticating with Spotify for creation permissions...")
                try:
                    sp = get_spotify_client()
                except Exception as e:
                    print(f"Authentication failed: {e}")
                    sys.exit(1)
            created_playlists = create_spotify_playlists(sp, proposed_playlists)
            if created_playlists:
                save_sorting_state(playlist_id, playlist_name, created_playlists)
            print("\nAll done!")
        else:
            print("\nPlaylist creation cancelled.")

if __name__ == "__main__":
    main()
