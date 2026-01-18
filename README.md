# Kickstarter Video Downloader

An advanced web scraper designed to download main campaign videos from Kickstarter project pages. This tool implements multiple bypass techniques to handle 403 errors and Cloudflare protection, with optional audio extraction capabilities.

## Overview

This scraper extracts and downloads the main campaign video from Kickstarter projects using a CSV file containing project URLs. It features multiple fallback methods to bypass web protection mechanisms and can optionally extract audio (MP3) from downloaded videos.

## Key Features

### Multi-Method Fetching
The scraper employs four different fetching methods to handle access restrictions:
- **Cloudscraper**: Automatic Cloudflare bypass
- **Enhanced Requests**: Rotating user agents and headers
- **Selenium Chrome**: Undetected Chrome with stealth mode and JavaScript enabled
- **Firefox Fallback**: Alternative browser for additional reliability

### Simplified Video Extraction
The scraper specifically targets the main campaign video only by extracting it from the `window.current_project` JSON object embedded in the page HTML. This focused approach:
- Extracts only the primary campaign video (not related or update videos)
- Prioritizes high-quality video URLs when available
- Falls back to base quality if high quality is unavailable

### Audio Extraction
Optional MP3 audio extraction using MoviePy:
- Converts downloaded videos to MP3 format
- Saves audio files to a separate `audio/` subdirectory
- Automatically skips conversion if MP3 already exists
- Detects and reports videos without audio tracks

### Rate Limiting Protection
- Smart wait logic: 15-30 second delays between requests
- Respects processing time (only waits for remaining time if needed)
- Helps avoid IP bans and rate limiting

### Organized Output
- Videos saved to: `[download_dir]/videos/`
- Audio files saved to: `[download_dir]/audio/`
- Comprehensive logging to: `[download_dir]/logs/`

## Requirements

### Software Dependencies
- Python 3.7 or higher
- Google Chrome (for Selenium-based fetching)
- Firefox (optional, for fallback method)
- FFmpeg (required for audio extraction)

### Python Packages
All required packages are listed in `requirements.txt`:
- requests
- beautifulsoup4
- selenium
- undetected-chromedriver
- cloudscraper
- moviepy
- (see requirements.txt for complete list)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/IRI-Kickstarter-Video-downloads.git
cd IRI-Kickstarter-Video-downloads
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg (Required for Audio Extraction)
**Windows:**
- Download from: https://ffmpeg.org/download.html
- Add FFmpeg to your system PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

## Usage

### Prepare Your CSV File

The scraper expects a CSV file with the following columns:
- `id`: Project ID (required)
- `url`: Full Kickstarter project URL (required)
- `launched_at`: Launch date (optional)
- `state`: Project state (optional)

**Example CSV Format:**
```csv
id,url,launched_at,state
123456,https://www.kickstarter.com/projects/example/project-name,2024-01-01,successful
789012,https://www.kickstarter.com/projects/another/project-two,2024-02-01,successful
```

### Default CSV File

By default, the scraper looks for `non_disabled_matched_list.csv` in the same directory. If not found, it falls back to `Videos List.csv`.

### Run the Scraper

```bash
python scrapper.py
```

### Interactive Prompts

**1. Number of Projects:**
```
How many projects to process? (press Enter for 5, or type 'all'):
```
- Press **Enter**: Process first 5 projects (default/testing)
- Type **'all'**: Process all projects in CSV
- Type a **number**: Process that many projects

**2. Audio Extraction:**
```
Do you want to extract audio (MP3) as well? (y/n, default n):
```
- Type **'y'**: Enable audio extraction
- Press **Enter** or type **'n'**: Video download only

## Output Structure

```
download_directory/
├── videos/
│   ├── [project_id]_[project_title].mp4
│   ├── [project_id]_[project_title].mp4
│   └── ...
├── audio/
│   ├── [project_id]_[project_title].mp3
│   ├── [project_id]_[project_title].mp3
│   └── ...
└── logs/
    ├── advanced_downloads_[timestamp].json
    └── advanced_errors_[timestamp].log
```

### File Naming Convention
Files are named using the format: `[project_id]_[sanitized_project_title].[extension]`

Example: `123456_Revolutionary_New_Product.mp4`

## Configuration

### Using a Custom CSV File

To use a different CSV file, modify line 626 in `scrapper.py`:

```python
csv_file = "non_disabled_matched_list.csv"  # Change this to your filename
```

### Changing the Download Directory

To change where files are saved, modify line 28 in `scrapper.py`:

```python
def __init__(self, csv_file, download_dir="non_disabled_matched_list"):
    # Change "non_disabled_matched_list" to your preferred directory name
```

Or pass it directly when creating the downloader instance (line 636):

```python
downloader = AdvancedKickstarterDownloader(csv_file, download_dir="my_custom_directory")
```

### Adjusting Rate Limits

To modify the delay between requests, change line 593 in `scrapper.py`:

```python
target_delay = 15 + random.random() * 15  # Currently 15-30 seconds
```

## How It Works

### 1. CSV Processing
The scraper reads project information from the CSV file, including project IDs and URLs.

### 2. Page Fetching
For each project URL, the scraper attempts to fetch the page content using multiple methods in sequence:
1. Cloudscraper (fastest, handles Cloudflare)
2. Enhanced requests (rotating headers)
3. Selenium Chrome (JavaScript-enabled, stealth mode)
4. Firefox (fallback browser)

The first successful method is used, and others are skipped.

### 3. Video Extraction
The scraper parses the HTML to find the `window.current_project` JSON object, which contains:
- Project metadata
- Main campaign video information
- Video URLs in different quality levels

It extracts the highest quality video URL available (high quality preferred, base quality as fallback).

### 4. Video Download
Videos are downloaded using:
- Direct download for standard MP4 URLs
- yt-dlp for YouTube/Vimeo embeds (if present)
- Cloudscraper or requests session for download

### 5. Audio Extraction (Optional)
If enabled, the scraper:
- Loads the downloaded video with MoviePy
- Extracts the audio track
- Saves it as MP3 in the audio directory
- Handles videos without audio tracks gracefully

### 6. Smart Wait Logic
After each project:
- Calculates total processing time
- Waits for remaining time to meet 15-30 second target
- Proceeds immediately if processing already took longer than target

## Statistics and Logging

### Download Log
Location: `[download_dir]/logs/advanced_downloads_[timestamp].json`

Contains:
- Total projects processed
- Videos found
- Videos successfully downloaded
- Projects with videos
- Projects skipped
- Error details

### Error Log
Location: `[download_dir]/logs/advanced_errors_[timestamp].log`

Records detailed error information for troubleshooting.

## Troubleshooting

### 403 Forbidden Errors
If you still encounter 403 errors:
- Increase delays between requests (modify line 593)
- Process smaller batches over multiple sessions
- Use a VPN or proxy service
- Try running during off-peak hours

### Chrome Driver Issues
```bash
pip install --upgrade undetected-chromedriver
```

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### FFmpeg Not Found
Ensure FFmpeg is installed and added to your system PATH. Verify installation:
```bash
ffmpeg -version
```

### No Audio Track Found
Some Kickstarter videos may not contain audio tracks. The scraper will detect this and skip audio extraction for those files.

## Best Practices

### Rate Limiting
- Default delays (15-30 seconds) are conservative
- Processing large batches may still trigger rate limiting
- Consider splitting large CSV files into smaller batches
- Space out batch processing over multiple days if needed

### CSV File Requirements
- Ensure `id` and `url` columns are present
- Remove duplicate project IDs before processing
- Verify all URLs are valid Kickstarter project pages

### Disk Space
- Estimate approximately 50-200 MB per video
- Audio files are typically 3-10 MB each
- Ensure adequate free space before processing large batches

## Technical Details

### Stealth Features
- Undetected ChromeDriver to bypass bot detection
- JavaScript enabled for dynamic content loading
- User agent rotation
- Realistic browser behavior (scrolling, waiting)
- Cookie handling
- Cloudflare bypass via cloudscraper

### Video Quality Priority
1. High quality (preferred)
2. Base quality (fallback)

### Supported Video Sources
- Direct MP4 URLs
- YouTube embeds (via yt-dlp)
- Vimeo embeds (via yt-dlp)
- Other video formats (.webm, .mov)

## Reproducibility

To reproduce the scraping process:

1. **Set up environment**:
   ```bash
   git clone [repository_url]
   cd IRI-Kickstarter-Video-downloads
   pip install -r requirements.txt
   ```

2. **Install FFmpeg** (follow installation instructions above)

3. **Prepare CSV file** with required columns (`id`, `url`)

4. **Run the scraper**:
   ```bash
   python scrapper.py
   ```

5. **Follow prompts** to specify number of projects and audio extraction preference

6. **Monitor output** in console and check logs for any issues

7. **Locate files** in the designated download directory


