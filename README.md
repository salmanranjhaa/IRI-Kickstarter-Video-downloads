# Kickstarter Video Scraper + Transcription Pipeline

This repository currently contains a 2-stage workflow:

1. Run `scrapper.py` locally to download Kickstarter campaign videos (and optionally extract MP3 audio).
2. Run `Transcription (via collab).ipynb` in Google Colab to transcribe the MP3 files.

The README below reflects the latest versions of:
- `scrapper.py`
- `Transcription (via collab).ipynb`
- `transcribe.py`
- `transcribe_status.py`

## What The Scraper Currently Does

`scrapper.py`:
- Reads project rows from CSV (`id`/`url` or `ID`/`Url` columns).
- Fetches each Kickstarter page with fallback methods:
  - cloudscraper
  - enhanced `requests`
  - Selenium + undetected Chrome
  - Selenium Firefox fallback
- Extracts only the main campaign video from `window.current_project` JSON.
- Downloads the video into `videos/`.
- Optionally converts to MP3 into `audio/`.
- Writes logs under `logs/`.
- Supports resume behavior by skipping project IDs already found in existing `videos/` or `audio/` file names.
- Uses smart per-project throttling (target 15-30 seconds total per project including work time).

## End-To-End Workflow

1. Run the scraper locally (with audio extraction enabled).
2. Upload generated MP3 files to Google Drive.
3. Run the Colab notebook to transcribe and save `transcriptions.csv`.
4. Download/use the output CSV.

## Local Setup (Scraper)

### Prerequisites

- Windows machine (script paths are currently Windows-style by default).
- Python environment managed by `uv`.
- Chrome installed (for Selenium fallback path).
- FFmpeg installed (required if MP3 extraction is enabled).
- Optional:
  - Firefox + geckodriver (only used if Chrome path fails).
  - `yt-dlp` (used for YouTube/Vimeo URLs).

### Install dependencies

```powershell
uv sync
```

## Run The Scraper Locally

### 1. Configure input/output paths in `scrapper.py`

In `main()`, update these two values:

```python
csv_file = r"E:\temp\uncovered_march\uncovered_individual_nondisabled_list.csv"
download_dir = r"E:\temp\uncovered_march\Output"
```

Use paths that exist on your machine.

### 2. Ensure CSV format

Required columns:
- `id` and `url`

Also accepted:
- `ID` and `Url`

### 3. Run

```powershell
uv run scrapper.py
```

Interactive prompts:
- Number of projects:
  - press Enter -> first 5
  - enter `all` -> all rows
  - enter number -> first N rows
- Audio extraction:
  - `y` -> extract MP3
  - Enter or `n` -> video only

### 4. Output structure

Under your configured `download_dir`:

```text
[download_dir]/
  videos/
  audio/
  logs/
```

## Transcribe In Google Colab (Recommended)

Use `Transcription (via collab).ipynb`.

### 1. Upload audio to Google Drive

Upload the scraper-generated MP3 files (`[download_dir]/audio/*.mp3`) to your Drive folder.

### 2. Open notebook in Colab

Open `Transcription (via collab).ipynb` in Google Colab.

### 3. Select GPU runtime

In Colab:
- Runtime -> Change runtime type -> GPU

### 4. Update notebook paths (Cell that defines `AUDIO_DIR`/`OUTPUT_DIR`)

Set these to your Drive locations:

```python
AUDIO_DIR  = "/content/drive/MyDrive/Audio Transcription/Audio_last/audio"
OUTPUT_DIR = "/content/drive/MyDrive/Audio Transcription/Output"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "transcriptions.csv")
```

### 5. Run all cells top-to-bottom

Notebook behavior:
- Installs Whisper/HuggingFace dependencies.
- Mounts Google Drive.
- Loads `openai/whisper-large-v3`.
- Copies audio files to local Colab disk cache (`/content/audio_cache`) for faster reads.
- Uses checkpoint CSV resume logic:
  - If `OUTPUT_CSV` exists, IDs already in CSV are skipped.
- Transcribes in batches (`BATCH_SIZE = 16`).
- If a batch fails, it falls back to file-by-file for that batch.
- Appends each finished batch immediately to CSV to reduce loss on session interruption.

### 6. Collect output

Final output file:
- `OUTPUT_CSV` (columns: `ID`, `original_file_name`, `transcribed_text`)

## Local Transcription Scripts (Alternative)

### `transcribe.py`

This is a Groq-based transcription runner with:
- 20 RPM pacing (`MIN_DELAY = 3s`)
- 429 exponential backoff retries
- resume state from legacy + current CSV
- retry queue for previous errors
- polling loop mode

Before running:
- Update `INPUT_CSV`, `AUDIO_DIR`, `LEGACY_CSV`, `OUTPUT_CSV` constants.
- Set a valid Groq API key (do not commit secrets).

Run:

```powershell
uv run transcribe.py
```

### `transcribe_status.py`

Status dashboard for transcription progress.

Run once:

```powershell
uv run transcribe_status.py
```

Auto-refresh mode:

```powershell
uv run transcribe_status.py --watch
```

## Logic Check Notes

I checked the latest script logic against the code in this repo:

- Scraper resume logic is ID-based from existing output file names.
- Scraper currently requires editing hardcoded path values in `main()` before running.
- Colab notebook transcription is checkpointed and resumable by `ID` in `transcriptions.csv`.
- Local Groq transcription scripts are path-config driven and should be updated per dataset before use.

## Quick Start (Practical)

1. Edit `scrapper.py` paths in `main()`.
2. Run `uv run scrapper.py` and choose `y` for MP3 extraction.
3. Upload `[download_dir]/audio` to Google Drive.
4. Open `Transcription (via collab).ipynb` in Colab and update `AUDIO_DIR`/`OUTPUT_DIR`.
5. Run all cells and collect `transcriptions.csv` from Drive.
