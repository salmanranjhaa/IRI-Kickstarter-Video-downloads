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

    def extract_videos_comprehensive(self, soup, project_url):
        """Comprehensive video extraction with all methods"""
        videos = []

        # 1. Find video HTML tags
        for video in soup.find_all('video'):
            src = video.get('src')
            if src:
                full_url = urljoin(project_url, src)
                videos.append({'type': 'video_tag', 'url': full_url})

            # Check source tags within video elements
            for source in video.find_all('source'):
                src = source.get('src')
                if src:
                    full_url = urljoin(project_url, src)
                    videos.append({'type': 'source_tag', 'url': full_url})

        # 2. Look for iframe embeds (YouTube, Vimeo, etc.)
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            if src:
                full_src = urljoin(project_url, src)
                if any(x in full_src.lower() for x in ['youtube', 'youtu.be', 'vimeo', 'kickstarter', 'loom', 'wistia', 'video']):
                    videos.append({'type': 'iframe', 'url': full_src})

        # 3. Find direct video links in href attributes
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            full_href = urljoin(project_url, href)
            if any(ext in full_href.lower() for ext in ['.mp4', '.webm', '.mov', '.avi', '.mkv', '.flv']):
                videos.append({'type': 'direct_link', 'url': full_href})

        # 4. Search for video URLs in data attributes and all attributes
        for elem in soup.find_all(True):
            for attr, value in elem.attrs.items():
                if isinstance(value, str) and value.strip():
                    lower_value = value.lower()
                    if any(ext in lower_value for ext in ['.mp4', '.webm', '.mov', '.avi', '.mkv', '.flv']):
                        if not value.startswith('data:'):  # Skip data URIs
                            full_url = urljoin(project_url, value)
                            videos.append({'type': 'data_attribute', 'url': full_url})

        # 5. Search for URLs in script tags (video config, JSON data)
        for script in soup.find_all('script'):
            if script.string:
                script_text = script.string
                if any(keyword in script_text.lower() for keyword in ['mp4', 'webm', 'video', 'youtube', 'vimeo']):
                    # Extract URLs using regex
                    patterns = [
                        r'https?://[^\s"\'<>]+\.(?:mp4|webm|mov|avi|mkv|flv)[^\s"\'<>]*',
                        r'https?://(?:www\.)?(?:youtube\.com|youtu\.be|vimeo\.com|kickstarter\.com)/[^\s"\'<>]*',
                        r'"(https?://[^\s"\'<>]+\.(?:mp4|webm|mov|avi|mkv|flv)[^\s"\'<>]*)"',
                        r"'(https?://[^\s\"'<>]+\.(?:mp4|webm|mov|avi|mkv|flv)[^\s\"'<>]*)'"
                    ]

                    for pattern in patterns:
                        urls = re.findall(pattern, script_text)
                        for url in urls:
                            if isinstance(url, tuple):
                                url = url[0]
                            videos.append({'type': 'script', 'url': url})

        # 6. Look for JSON-LD structured data
        for script in soup.find_all('script', {'type': 'application/ld+json'}):
            if script.string:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if 'video' in data:
                            video_data = data['video']
                            if isinstance(video_data, dict) and 'contentUrl' in video_data:
                                videos.append({'type': 'json_ld', 'url': video_data['contentUrl']})
                            elif isinstance(video_data, list):
                                for v in video_data:
                                    if isinstance(v, dict) and 'contentUrl' in v:
                                        videos.append({'type': 'json_ld', 'url': v['contentUrl']})
                except:
                    pass

        # 7. Look for video data in other JSON scripts
        for script in soup.find_all('script', {'type': 'application/json'}):
            if script.string:
                try:
                    data = json.loads(script.string)
                    self._extract_from_json(data, videos, project_url)
                except:
                    pass

        # 8. Look for Open Graph video meta tags
        for meta in soup.find_all('meta', {'property': True}):
            prop = meta.get('property', '')
            content = meta.get('content', '')
            if prop in ['og:video', 'og:video:url', 'og:video:secure_url'] and content:
                videos.append({'type': 'open_graph', 'url': content})

        # 9. Look for video URLs in regular meta tags
        for meta in soup.find_all('meta'):
            content = meta.get('content', '')
            if content and any(ext in content.lower() for ext in ['.mp4', '.webm', '.mov']):
                if content.startswith('http'):
                    videos.append({'type': 'meta_tag', 'url': content})

        return self._deduplicate_videos(videos)

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

            # Extract videos
            videos = self.extract_videos_comprehensive(soup, project_url)

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

    def download_video(self, video_info, project_folder):
        """Download video using appropriate method"""
        video_url = video_info['url']
        video_type = video_info['type']

        try:
            if not os.path.exists(project_folder):
                os.makedirs(project_folder)

            if 'youtube' in video_url or 'youtu.be' in video_url:
                return self._download_with_ytdlp(video_url, project_folder, 'youtube')
            elif 'vimeo' in video_url:
                return self._download_with_ytdlp(video_url, project_folder, 'vimeo')
            else:
                return self._download_direct_enhanced(video_url, project_folder)

        except Exception as e:
            print(f"Download error: {e}")
            return False

    def _download_with_ytdlp(self, video_url, project_folder, service):
        """Download with yt-dlp"""
        try:
            output_template = os.path.join(project_folder, f'{service}_%(title)s.%(ext)s')

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

    def _download_direct_enhanced(self, video_url, project_folder):
        """Enhanced direct download"""
        try:
            parsed = urlparse(video_url)
            filename = os.path.basename(parsed.path) or f"video_{int(time.time())}.mp4"
            filepath = os.path.join(project_folder, filename)

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
                    print("No videos found")
                    self.stats['projects_skipped'] += 1
                    continue

                self.stats['projects_with_videos'] += 1
                self.stats['videos_found'] += len(project_info['videos'])

                print(f"Found {len(project_info['videos'])} video(s)")

                project_folder = os.path.join(self.download_dir, project_info['safe_title'])

                for video_idx, video_info in enumerate(project_info['videos'], 1):
                    print(f"  [{video_idx}/{len(project_info['videos'])}] Downloading: {video_info['type']}")

                    if self.download_video(video_info, project_folder):
                        self.stats['videos_downloaded'] += 1
                        print("    Success")
                    else:
                        print("    Failed")

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
    csv_file = "D:/Personal/Work/IRI/Video Downloads/Videos List.csv"

    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        # Try current directory
        csv_file = "Videos List.csv"
        if not os.path.exists(csv_file):
            print("CSV file not found in current directory either")
            return

    downloader = AdvancedKickstarterDownloader(csv_file)

    print("=" * 70)
    print("ADVANCED KICKSTARTER VIDEO DOWNLOADER")
    print("=" * 70)
    print("Features:")
    print("  - Multiple bypass techniques for 403 errors")
    print("  - Cloudscraper for Cloudflare bypass")
    print("  - Enhanced Selenium with JavaScript ENABLED")
    print("  - Firefox fallback")
    print("  - Comprehensive video extraction (9 methods)")
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