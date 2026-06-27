# Spotify Playlist Sorter

An intelligent, stateful Spotify utility that reads a playlist and sorts its tracks into smaller, vibe-categorized sub-playlists using AI grouping recommendations from the Antigravity CLI (`agy`).

It supports full, initial sorting as well as smart **incremental syncs**—allowing you to add or remove tracks in your source playlist and cleanly update your target playlists without duplication.

---

## Features

- **Spotify Web API Compliance**: Implements the modern `/v1/playlists/{id}/items` and `/v1/me/playlists` endpoints, bypassing deprecated endpoints to ensure reliable operations.
- **AI-Powered Categorization**: Leverages the Antigravity CLI (`agy`) to analyze track metadata and logically group them by genre, vibe, or energy.
- **Custom Sort Queries**: Direct the AI's sorting criteria using customized rules (e.g., `group by decade` or `separate into chill pop, acoustic, and high-energy rock`).
- **Stateful Incremental Syncing**: Saves sorting state files in a local `states/` directory (tracked under Git). Subsequent runs identify additions or removals on the source playlist, letting you incrementally update your sorted sub-playlists on Spotify.
- **Out-of-Sync Verification**: Automatically detects if you've made manual modifications to target playlists directly on Spotify. Offers choices to either revert Spotify to match your local state or update your local state to adopt your Spotify changes.
- **Timestamps**: Programmatically maintains a `(Last sorted: YYYY-MM-DD HH:MM)` tag at the end of every sub-playlist's description, keeping you informed of when edits occurred.
- **NixOS Dev Support**: Native, reproducible development environment via `shell.nix`.

---

## Project Structure

- **[spotify_sorter.py](file:///home/dchan/personal-work/spotifySorter/spotify_sorter.py)**: The main script handling Spotify Web API requests, CLI parsing, AI prompt formatting, diffing logic, and state management.
- **[shell.nix](file:///home/dchan/personal-work/spotifySorter/shell.nix)**: The Nix shell configuration pinning Python and its dependencies (`spotipy` and `python-dotenv`).
- **[requirements.txt](file:///home/dchan/personal-work/spotifySorter/requirements.txt)**: Python package dependencies (for non-Nix users).
- **[states/](file:///home/dchan/personal-work/spotifySorter/states/)**: Dedicated folder tracking the sorted track states mapped to their Spotify playlist IDs.
- **[playlist_tracks.json](file:///home/dchan/personal-work/spotifySorter/playlist_tracks.json)**: Cache containing details of the last fetched playlist (excluded from version control).

---

## Setup Instructions

### 1. Create a Spotify Developer App
1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and log in.
2. Click **Create App** and fill in the details.
3. **Critical**: Set **Redirect URI** to `http://localhost:8888/callback`.
4. Go to **Settings** and retrieve your **Client ID** and **Client Secret**.

### 2. Configure Environment Variables
Copy `.env.template` to `.env` and fill in your developer credentials:
```bash
cp .env.template .env
```

### 3. Enter Environment
Choose one of the two options depending on your setup:

- **Option A: NixOS (`nix-shell`)** — *Recommended*
  ```bash
  nix-shell
  ```
- **Option B: Traditional Python Virtual Environment**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

---

## Usage Guide

### Step 1: Capture & Cache Playlist Details
Fetches all track data, handling Spotify pagination, and saves a local cache:
```bash
python spotify_sorter.py https://open.spotify.com/playlist/YOUR_PLAYLIST_ID_HERE
```
*Note: On your first run, your browser will open to ask you to authorize your app.*

### Step 2: Sort the Tracks
Run the script in sorting mode. You can load directly from your cache instead of fetching Spotify again:
```bash
# Let AI automatically decide the categories
python spotify_sorter.py --sort

# Or specify custom sorting instructions
python spotify_sorter.py --query "group by decade"
```
The script will display a preview of the proposed sub-playlists. Type `y` when prompted to create them as **private playlists** on your Spotify account.

### Step 3: Run Incremental Syncs
If you add or delete tracks in your source playlist over time, simply re-run standard capture. The script will compare the updated source tracks against your saved states under `states/` and output a diff:
```bash
python spotify_sorter.py https://open.spotify.com/playlist/YOUR_PLAYLIST_ID_HERE
```
It will guide you through:
1. **Cleanups**: Removing any tracks on Spotify that were deleted from the source playlist.
2. **Incremental Sorting**: Sending *only* the new tracks to `agy` along with a list of your existing categories to place them.
3. **Sync Reconciliation**: Prompting you to revert or accept changes if the sorted playlists on Spotify were edited manually.
