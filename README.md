# Kickstarter Video Downloader

An advanced web scraper for downloading videos from Kickstarter project pages. This tool uses multiple bypass techniques to handle 403 errors and Cloudflare protection, with comprehensive video extraction methods.

## Features

- **Multiple Bypass Techniques**: Handles 403 Forbidden errors with 4 different fetching methods
  - Cloudscraper (Cloudflare bypass)
  - Enhanced requests with rotating user agents
  - Selenium Chrome with stealth mode
  - Firefox fallback

- **Comprehensive Video Extraction**: Uses 9 different methods to find videos
  - Video HTML tags
  - Source tags within video elements
  - iFrame embeds (YouTube, Vimeo, etc.)
  - Direct video links
  - Data attributes
  - Script tags with video URLs
  - JSON-LD structured data
  - Open Graph meta tags
  - Regular meta tags

- **Rate Limiting Protection**: 15-30 second delays between requests
- **Progress Tracking**: Automatic checkpoints every 50 projects
- **Detailed Logging**: Comprehensive logs for troubleshooting
- **Resume Capability**: Can resume from interruptions

## Requirements

- Python 3.7+
- Chrome browser (for Selenium)
- Firefox browser (optional, for fallback)
- yt-dlp (optional, for YouTube/Vimeo downloads)

## Installation

1. Clone or download this repository

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install yt-dlp (optional, for YouTube/Vimeo support):
```bash
pip install yt-dlp
```

Or download from: https://github.com/yt-dlp/yt-dlp

## Usage

1. Prepare your CSV file with Kickstarter project URLs. The CSV should have these columns:
   - `id`: Project ID
   - `url`: Project URL
   - `launched_at`: Launch date (optional)
   - `state`: Project state (optional)

2. Update the CSV file path in `scrapper.py` (line 447):
```python
csv_file = "path/to/your/Videos List.csv"
```

3. Run the script:
```bash
python scrapper.py
```

4. When prompted, choose how many projects to process:
   - Press **Enter** for 5 projects (test mode)
   - Type **'all'** to process all projects
   - Type a **number** for specific amount

##  Instructions (Using your own CSV)

If you have a different CSV file you want to use:

1. **Place your CSV file** in the SAME folder as `scrapper.py`.
2. Open `scrapper.py` in a text editor (Notepad, VS Code, etc.).
3. Scroll down to the bottom (around **line 562**) to find this line:
   ```python
   csv_file = "random_50_projects.csv"
   ```
4. Change `"random_50_projects.csv"` to your exact filename (e.g., `"My_Project_List.csv"`).
5. **Save the file** and run the script again.

**IMPORTANT: Your CSV file MUST have these two columns:**
- `id` (The project ID)
- `url` (The link to the Kickstarter page)


## Output

### Downloaded Videos
Videos are saved to: `kickstarter_downloads/`

### Logs
Logs are saved to: `kickstarter_downloads/logs/`
- `advanced_downloads_[timestamp].json` - Detailed statistics
- `advanced_errors_[timestamp].log` - Error logs
- `progress.json` - Resume checkpoint

## Configuration

### Adjust Delays
To change the delay between requests, modify line 423 in `scrapper.py`:
```python
delay = 15 + random.random() * 15  # 15-30 seconds
```

### Change Download Directory
Modify the `download_dir` parameter when creating the downloader:
```python
downloader = AdvancedKickstarterDownloader(csv_file, download_dir="custom_directory")
```

## Troubleshooting

### Still Getting 403 Errors
- Increase the delay between requests (change line 423)
- Try running during off-peak hours
- Consider using a VPN or proxy
- Process smaller batches with longer breaks

### Chrome Driver Issues
If you get Chrome driver errors:
```bash
pip install --upgrade undetected-chromedriver
```

### Missing Dependencies
If you get import errors:
```bash
pip install -r requirements.txt --upgrade
```

## Important Notes

### Rate Limiting
- Default: 15-30 seconds between projects
- Kickstarter may still block you if processing too many projects
- Consider processing in smaller batches over multiple days


## File Structure

```
.
├── scrapper.py          # Main script
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── Videos List.csv               # Your input CSV
└── kickstarter_downloads/        # Output directory
    └── video files
    └── logs/                     # Log files
        ├── advanced_downloads_*.json
        ├── advanced_errors_*.log
        └── progress.json
```

## Statistics

The script tracks:
- Total projects processed
- Videos found
- Videos successfully downloaded
- Projects skipped (no videos)
- Errors encountered

View statistics in: `kickstarter_downloads/logs/advanced_downloads_[timestamp].json`

## Example CSV Format

```csv
id,url,launched_at,state
123456,https://www.kickstarter.com/projects/example/project-name,2024-01-01,successful
789012,https://www.kickstarter.com/projects/another/project-two,2024-02-01,successful
