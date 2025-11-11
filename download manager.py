import os
import json
import csv
from pathlib import Path
from datetime import datetime


class DownloadManager:
    def __init__(self, download_dir="kickstarter_downloads"):
        self.download_dir = download_dir
        self.log_dir = os.path.join(download_dir, "logs")
    
    def get_latest_log(self):
        """
        I retrieve the most recent download log file.
        """
        if not os.path.exists(self.log_dir):
            print("I found no logs directory")
            return None
        
        log_files = [f for f in os.listdir(self.log_dir) if f.startswith('downloads_')]
        if not log_files:
            print("I found no download logs")
            return None
        
        latest = sorted(log_files)[-1]
        return os.path.join(self.log_dir, latest)
    
    def get_progress(self):
        """
        I check if there's a progress checkpoint to resume from.
        """
        progress_file = os.path.join(self.log_dir, "progress.json")
        
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                progress = json.load(f)
            return progress
        
        return None
    
    def print_stats(self):
        """
        I print statistics about the download process.
        """
        log_file = self.get_latest_log()
        
        if not log_file:
            print("I found no statistics available")
            return
        
        with open(log_file, 'r') as f:
            stats = json.load(f)
        
        print("\n" + "="*60)
        print("DOWNLOAD STATISTICS")
        print("="*60)
        print(f"Total projects: {stats.get('total_projects', 0)}")
        print(f"Processed: {stats.get('processed', 0)}")
        print(f"Videos found: {stats.get('videos_found', 0)}")
        print(f"Videos downloaded: {stats.get('videos_downloaded', 0)}")
        print(f"Projects with videos: {stats.get('projects_with_videos', 0)}")
        print(f"Errors: {len(stats.get('errors', []))}")
        print("="*60)
    
    def list_downloaded_projects(self):
        """
        I list all projects that have downloaded videos.
        """
        if not os.path.exists(self.download_dir):
            print("I found no download directory")
            return
        
        projects = []
        for folder in os.listdir(self.download_dir):
            folder_path = os.path.join(self.download_dir, folder)
            
            if os.path.isdir(folder_path) and folder != "logs":
                video_count = len([f for f in os.listdir(folder_path) 
                                  if f.endswith(('.mp4', '.webm', '.mov', '.avi', '.mkv'))])
                
                if video_count > 0:
                    projects.append({
                        'folder': folder,
                        'video_count': video_count
                    })
        
        if not projects:
            print("I found no downloaded projects")
            return
        
        print(f"\nI found {len(projects)} projects with videos:")
        print("="*60)
        for proj in sorted(projects, key=lambda x: x['video_count'], reverse=True):
            print(f"  {proj['folder']}: {proj['video_count']} video(s)")
        print("="*60)
    
    def get_total_downloaded_videos(self):
        """
        I count the total number of videos downloaded.
        """
        total = 0
        
        if not os.path.exists(self.download_dir):
            return 0
        
        for root, dirs, files in os.walk(self.download_dir):
            for file in files:
                if file.endswith(('.mp4', '.webm', '.mov', '.avi', '.mkv')):
                    total += 1
        
        return total
    
    def get_total_size(self):
        """
        I calculate the total size of all downloaded videos.
        """
        total_size = 0
        
        if not os.path.exists(self.download_dir):
            return 0
        
        for root, dirs, files in os.walk(self.download_dir):
            for file in files:
                if file.endswith(('.mp4', '.webm', '.mov', '.avi', '.mkv')):
                    filepath = os.path.join(root, file)
                    total_size += os.path.getsize(filepath)
        
        return total_size
    
    def format_size(self, bytes_size):
        """
        I convert bytes to human-readable format.
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"
    
    def print_full_report(self):
        """
        I print a comprehensive download report.
        """
        print("\n" + "="*70)
        print("COMPREHENSIVE DOWNLOAD REPORT")
        print("="*70)
        
        self.print_stats()
        
        total_videos = self.get_total_downloaded_videos()
        total_size = self.get_total_size()
        
        print(f"\nTotal videos on disk: {total_videos}")
        print(f"Total size: {self.format_size(total_size)}")
        
        progress = self.get_progress()
        if progress:
            print(f"\nLast checkpoint: {progress.get('timestamp', 'Unknown')}")
            print(f"Last processed index: {progress.get('current_index', 'Unknown')}")
        
        print("="*70)
    
    def export_to_csv(self, output_file="download_report.csv"):
        """
        I export the download report to a CSV file.
        """
        if not os.path.exists(self.download_dir):
            print("I found no download directory")
            return
        
        rows = []
        
        for root, dirs, files in os.walk(self.download_dir):
            if root == self.log_dir:
                continue
            
            for file in files:
                if file.endswith(('.mp4', '.webm', '.mov', '.avi', '.mkv')):
                    filepath = os.path.join(root, file)
                    file_size = os.path.getsize(filepath)
                    
                    rows.append({
                        'project': os.path.basename(root),
                        'filename': file,
                        'size_bytes': file_size,
                        'size_mb': f"{file_size / (1024*1024):.2f}",
                        'path': filepath
                    })
        
        if not rows:
            print("I found no videos to export")
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['project', 'filename', 'size_bytes', 'size_mb', 'path'])
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"I exported {len(rows)} videos to: {output_file}")


def main():
    manager = DownloadManager()
    
    print("KICKSTARTER DOWNLOAD MANAGER")
    print("="*70)
    print("1. Print full report")
    print("2. List downloaded projects")
    print("3. Show statistics")
    print("4. Export to CSV")
    print("5. Check progress/resume point")
    print("6. Show disk space used")
    print("="*70)
    
    choice = input("\nI am waiting for your choice (1-6): ").strip()
    
    if choice == "1":
        manager.print_full_report()
    elif choice == "2":
        manager.list_downloaded_projects()
    elif choice == "3":
        manager.print_stats()
    elif choice == "4":
        manager.export_to_csv()
    elif choice == "5":
        progress = manager.get_progress()
        if progress:
            print(f"\nI found a checkpoint:")
            print(f"  Last processed index: {progress['current_index']}")
            print(f"  Timestamp: {progress['timestamp']}")
        else:
            print("\nI found no checkpoint")
    elif choice == "6":
        total_size = manager.get_total_size()
        total_videos = manager.get_total_downloaded_videos()
        print(f"\nI calculated the following:")
        print(f"  Total videos: {total_videos}")
        print(f"  Total size: {manager.format_size(total_size)}")
    else:
        print("I received an invalid choice")


if __name__ == "__main__":
    main()