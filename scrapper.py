import os
import csv
import json
import time
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import subprocess
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random
import cloudscraper


class AdvancedKickstarterDownloader:
    """
    Advanced downloader with multiple bypass techniques for 403 errors
    """

    def __init__(self, csv_file, download_dir="kickstarter_downloads"):
        self.csv_file = csv_file
        self.download_dir = download_dir

        # Initialize multiple session types
        self.requests_session = self._create_requests_session()
        self.cloudscraper_session = cloudscraper.create_scraper()

        # Create logging directory
        self.log_dir = os.path.join(download_dir, "logs")
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Initialize log files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.download_log = os.path.join(self.log_dir, f"advanced_downloads_{timestamp}.json")
        self.error_log = os.path.join(self.log_dir, f"advanced_errors_{timestamp}.log")

        self.stats = {
            'total_projects': 0,
            'processed': 0,
            'videos_found': 0,
            'videos_downloaded': 0,
            'projects_with_videos': 0,
            'projects_skipped': 0,
            'errors': []
        }

    def _create_requests_session(self):
        """Create a sophisticated requests session"""
        session = requests.Session()

        # Enhanced headers that mimic a real browser more closely
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.kickstarter.com/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Ch-Ua-Platform-Version': '"15.0.0"'
        }

        session.headers.update(headers)

        # Don't set fake cookies - let cloudscraper handle them automatically

        return session

    def fetch_with_multiple_methods(self, url):
        """
        Try multiple methods to fetch the page, each with different bypass techniques
        """
        methods = [
            self._fetch_with_cloudscraper,
            self._fetch_with_enhanced_requests,
            self._fetch_with_selenium_stealth,
            self._fetch_with_headless_firefox
        ]

        for method in methods:
            try:
                print(f"  Trying method: {method.__name__}")
                content = method(url)
                if content and len(content) > 1000:  # Basic content validation
                    print(f"  Success with {method.__name__}")
                    return content
            except Exception as e:
                print(f"  {method.__name__} failed: {e}")
                continue

        print("  All methods failed")
        return None

    def _fetch_with_cloudscraper(self, url):
        """Use cloudscraper to bypass Cloudflare protection"""
        response = self.cloudscraper_session.get(url, timeout=30)
        response.raise_for_status()
        return response.content

    def _fetch_with_enhanced_requests(self, url):
        """Enhanced requests with rotating headers and cookies"""
        # Rotate user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        ]

        self.requests_session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Referer': 'https://www.kickstarter.com/discover'
        })

        response = self.requests_session.get(url, timeout=20)
        response.raise_for_status()
        return response.content

    def _fetch_with_selenium_stealth(self, url):
        """Use Selenium with maximum stealth options - JavaScript ENABLED"""
        driver = None
        try:
            options = uc.ChromeOptions()
            options.add_argument('--headless=new')  # Use new headless mode
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            # REMOVED --disable-images to help with content loading
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            # JavaScript is ENABLED by default - don't disable it!

            driver = uc.Chrome(options=options, version_main=None)
            driver.set_window_size(1920, 1080)

            # Execute stealth scripts
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")

            driver.get(url)

            # Wait for initial page load
            time.sleep(5)

            # Try to accept cookies if present
            try:
                cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'accept')]")
                if cookie_buttons:
                    cookie_buttons[0].click()
                    time.sleep(1)
            except:
                pass

            # Scroll to load content and trigger lazy loading
            last_height = driver.execute_script("return document.body.scrollHeight")
            for i in range(10):
                driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(1)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Wait for video elements to load
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: len(d.find_elements(By.TAG_NAME, "video")) > 0 or
                              len(d.find_elements(By.TAG_NAME, "iframe")) > 0
                )
            except TimeoutException:
                print("    No video elements detected, but continuing...")

            # Additional wait for AJAX/dynamic content
            time.sleep(3)

            return driver.page_source.encode('utf-8')

        except Exception as e:
            raise e
        finally:
            if driver:
                driver.quit()

    def _fetch_with_headless_firefox(self, url):
        """Use Firefox as an alternative browser - JavaScript ENABLED"""
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService

        driver = None
        try:
            options = FirefoxOptions()
            options.add_argument('--headless')
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)
            options.set_preference("general.useragent.override",
                                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0")
            # JavaScript is enabled by default

            driver = webdriver.Firefox(options=options)
            driver.set_window_size(1920, 1080)
            driver.get(url)
            time.sleep(5)

            # Try to accept cookies
            try:
                cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'accept')]")
                if cookie_buttons:
                    cookie_buttons[0].click()
                    time.sleep(1)
            except:
                pass

            # Scroll to load content
            last_height = driver.execute_script("return document.body.scrollHeight")
            for i in range(8):
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Wait for videos
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: len(d.find_elements(By.TAG_NAME, "video")) > 0 or
                              len(d.find_elements(By.TAG_NAME, "iframe")) > 0
                )
            except TimeoutException:
                pass

            time.sleep(3)
            return driver.page_source.encode('utf-8')

        except Exception as e:
            raise e
        finally:
            if driver:
                driver.quit()

    def extract_main_video_only(self, soup, project_url):
        """Extract ONLY the main campaign video from the Kickstarter project JSON"""
        videos = []
        
        print("    Looking for main campaign video in page JSON...")
        
        # Find the script tag containing window.current_project
        for script in soup.find_all('script'):
            if script.string and 'window.current_project' in script.string:
                try:
                    import html as html_module
                    
                    script_text = script.string
                    
                    # Find the JSON string
                    start_marker = 'window.current_project = "'
                    start_idx = script_text.find(start_marker)
                    
                    if start_idx == -1:
                        continue
                    
                    start_idx += len(start_marker)
                    end_idx = script_text.find('";', start_idx)
                    
                    if end_idx == -1:
                        continue
                    
                    # Extract the JSON string and decode HTML entities
                    json_str = script_text[start_idx:end_idx]
                    json_str = html_module.unescape(json_str)
                    
                    # Instead of parsing the entire JSON (which has issues with escaped quotes),
                    # just use regex to extract the video URLs directly
                    
                    # Look for video object and extract ID
                    video_id_match = re.search(r'"video":\s*{\s*"id"\s*:\s*(\d+)', json_str)
                    video_id = video_id_match.group(1) if video_id_match else 'unknown'
                    
                    # Extract high quality URL
                    high_url_match = re.search(r'"high"\s*:\s*"(https://[^"]+\.mp4)"', json_str)
                    # Extract base quality URL  
                    base_url_match = re.search(r'"base"\s*:\s*"(https://[^"]+\.mp4)"', json_str)
                    
                    if high_url_match:
                        videos.append({
                            'type': 'main_campaign_video_high',
                            'url': high_url_match.group(1),
                            'quality': 'high',
                            'video_id': video_id
                        })
                        print(f"    Found main campaign video (ID: {video_id})")
                        print(f"    Video quality: HIGH")
                    elif base_url_match:
                        videos.append({
                            'type': 'main_campaign_video_base',
                            'url': base_url_match.group(1),
                            'quality': 'base',
                            'video_id': video_id
                        })
                        print(f"    Found main campaign video (ID: {video_id})")
                        print(f"    Video quality: BASE")
                    else:
                        print("    No video URLs found in project data")
                    
                    # Once we find window.current_project, we're done
                    break
                    
                except Exception as e:
                    print(f"    Error extracting video: {e}")
        
        if not videos:
            print("    No main campaign video found")
        
        return videos

    def _extract_from_json(self, data, videos, project_url):
        """Extract videos from JSON data structures"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and any(ext in value.lower() for ext in ['.mp4', '.webm', '.mov']):
                    if value.startswith('http'):
                        videos.append({'type': 'json_data', 'url': value})
                elif isinstance(value, (dict, list)):
                    self._extract_from_json(value, videos, project_url)
        elif isinstance(data, list):
            for item in data:
                self._extract_from_json(item, videos, project_url)

    def _deduplicate_videos(self, videos):
        """Remove duplicate videos"""
        unique_videos = []
        seen_urls = set()
        for video in videos:
            url = video['url'].strip()
            if url and url not in seen_urls:
                video['url'] = url
                unique_videos.append(video)
                seen_urls.add(url)
        return unique_videos

    def read_csv(self):
        """Read CSV file"""
        projects = []
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    projects.append({
                        'id': row.get('id'),
                        'url': row.get('url'),
                        'launched_at': row.get('launched_at'),
                        'state': row.get('state')
                    })

            self.stats['total_projects'] = len(projects)
            print(f"Loaded {len(projects)} projects from CSV")
            return projects

        except Exception as e:
            print(f"Error reading CSV: {e}")
            return []

    def scrape_project(self, project):
        """Scrape a single project using multiple methods"""
        try:
            project_url = project['url']
            print(f"Fetching: {project_url}")

            page_content = self.fetch_with_multiple_methods(project_url)

            if page_content is None:
                return None

            soup = BeautifulSoup(page_content, 'html.parser')

            # Extract title
            title_elem = soup.find('h1') or soup.find('title')
            project_title = title_elem.get_text(strip=True) if title_elem else f"project_{project['id']}"

            import re
            safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', project_title)[:60]

            # Extract ONLY the main campaign video
            videos = self.extract_main_video_only(soup, project_url)

            return {
                'id': project['id'],
                'title': project_title,
                'safe_title': safe_title,
                'url': project_url,
                'videos': videos,
                'state': project['state']
            }

        except Exception as e:
            print(f"Scraping error: {e}")
            return None

    def download_video(self, video_info, target_dir, filename_prefix):
        """Download video using appropriate method"""
        video_url = video_info['url']
        video_type = video_info['type']

        try:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            if 'youtube' in video_url or 'youtu.be' in video_url:
                return self._download_with_ytdlp(video_url, target_dir, filename_prefix)
            elif 'vimeo' in video_url:
                return self._download_with_ytdlp(video_url, target_dir, filename_prefix)
            else:
                return self._download_direct_enhanced(video_url, target_dir, filename_prefix)

        except Exception as e:
            print(f"Download error: {e}")
            return False

    def _download_with_ytdlp(self, video_url, target_dir, filename_prefix):
        """Download with yt-dlp"""
        try:
            output_template = os.path.join(target_dir, f'{filename_prefix}.%(ext)s')

            cmd = [
                'yt-dlp',
                '--no-check-certificates',
                '--ignore-errors',
                '--quiet',
                '-f', 'best[height<=720]',
                '-o', output_template,
                video_url
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0

        except Exception:
            return False

    def _download_direct_enhanced(self, video_url, target_dir, filename_prefix):
        """Enhanced direct download"""
        try:
            parsed = urlparse(video_url)
            # Use original extension if available, otherwise default to .mp4
            ext = os.path.splitext(parsed.path)[1]
            if not ext:
                ext = ".mp4"
            
            filename = f"{filename_prefix}{ext}"
            filepath = os.path.join(target_dir, filename)

            if os.path.exists(filepath):
                return True

            # Try with cloudscraper first
            try:
                response = self.cloudscraper_session.get(video_url, timeout=60, stream=True)
                response.raise_for_status()
            except:
                # Fallback to requests
                response = self.requests_session.get(video_url, timeout=60, stream=True)
                response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return os.path.exists(filepath) and os.path.getsize(filepath) > 0

        except Exception:
            return False

    def process_projects(self, max_projects=None):
        """Process all projects"""
        projects = self.read_csv()

        if not projects:
            return

        for idx, project in enumerate(projects[:max_projects], 1):
            print(f"\n[{idx}/{len(projects)}] Processing project ID: {project['id']}")

            try:
                project_info = self.scrape_project(project)

                if not project_info:
                    self.stats['projects_skipped'] += 1
                    continue

                if not project_info['videos']:
                    print("No main campaign video found")
                    self.stats['projects_skipped'] += 1
                    continue

                self.stats['projects_with_videos'] += 1
                self.stats['videos_found'] += len(project_info['videos'])

                print(f"Found main campaign video")

                # Download the main video (should only be one)
                video_info = project_info['videos'][0]
                print(f"  Downloading: {video_info.get('quality', 'unknown')} quality")

                # Save directly to download directory with project title as filename
                if self.download_video(video_info, self.download_dir, project_info['safe_title']):
                    self.stats['videos_downloaded'] += 1
                    print("    ✓ Download successful")
                else:
                    print("    ✗ Download failed")

                self.stats['processed'] += 1

                # Longer delay to avoid rate limiting (15-30 seconds)
                delay = 15 + random.random() * 15
                print(f"\n  Waiting {delay:.1f} seconds before next project...")
                time.sleep(delay)

            except KeyboardInterrupt:
                print("Interrupted by user")
                break

            except Exception as e:
                print(f"Error: {e}")
                self.stats['errors'].append({'project_id': project['id'], 'error': str(e)})

        self._save_results()

    def _save_results(self):
        """Save final results"""
        with open(self.download_log, 'w') as f:
            json.dump(self.stats, f, indent=2)

        print(f"\nResults saved to: {self.download_log}")
        print(f"Total processed: {self.stats['processed']}")
        print(f"Videos found: {self.stats['videos_found']}")
        print(f"Videos downloaded: {self.stats['videos_downloaded']}")


def main():
    # Using test CSV with 10 random projects
    csv_file = "random_50_projects.csv"

    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        # Try current directory
        csv_file = "Videos List.csv"
        if not os.path.exists(csv_file):
            print("CSV file not found in current directory either")
            return

    downloader = AdvancedKickstarterDownloader(csv_file)

    print("==" * 70)
    print("ADVANCED KICKSTARTER VIDEO DOWNLOADER")
    print("=" * 70)
    print("Features:")
    print("  - Multiple bypass techniques for 403 errors")
    print("  - Cloudscraper for Cloudflare bypass")
    print("  - Enhanced Selenium with JavaScript ENABLED")
    print("  - Firefox fallback")
    print("  - Extracts ONLY the main campaign video (not related videos)")
    print("  - Rate limiting protection (15-30s delays)")
    print("=" * 70)
    print(f"CSV file: {csv_file}")
    print(f"Download directory: {downloader.download_dir}")
    print("=" * 70)

    # Ask user how many projects to process
    try:
        user_input = input("\nHow many projects to process? (press Enter for 5, or type 'all'): ").strip()
        if user_input.lower() == 'all':
            max_projects = None
            print("Processing ALL projects from CSV...")
        elif user_input == '':
            max_projects = 5
            print("Processing first 5 projects...")
        else:
            max_projects = int(user_input)
            print(f"Processing first {max_projects} projects...")
    except:
        max_projects = 5
        print("Processing first 5 projects (default)...")

    print("\nStarting in 3 seconds... (Press Ctrl+C to cancel)")
    time.sleep(3)

    downloader.process_projects(max_projects=max_projects)


if __name__ == "__main__":
    main()