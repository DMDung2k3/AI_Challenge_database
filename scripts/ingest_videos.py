# scripts/ingest_videos.py

import sys
import os
from datetime import datetime

# Ensure project root is on sys.path for imports
SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Now imports from your project work:
from database.connections.metadata_db import get_session
from database.models.video_metadata import VideoMetadata
from bloom_filter2 import BloomFilter


def get_video_duration(path: str) -> float:
    # TODO: Replace with actual logic (e.g., ffprobe) to get video duration
    return 0.0


def ingest_folder(folder_path: str, user_id: int):
    """
    Ingest all video files in a folder:
      1) Insert metadata into PostgreSQL
      2) Build & store a Bloom filter based on filename tokens
    """
    db = get_session()
    try:
        for fname in os.listdir(folder_path):
            if not fname.lower().endswith(('.mp4', '.avi', '.mkv')):
                continue

            full_path = os.path.join(folder_path, fname)

            # 1) Create metadata record
            vm = VideoMetadata(
                user_id=user_id,
                filename=fname,
                duration=get_video_duration(full_path),
                upload_time=datetime.utcnow()
            )
            db.add(vm)
            db.commit()
            db.refresh(vm)

            # 2) Build simple BloomFilter from filename tokens
            bf = BloomFilter(max_elements=10000, error_rate=0.01)
            for token in fname.replace('.', ' ').split():
                bf.add(token.lower())

            # 3) Store Bloom filter bytes in the record
            vm.bloom_filter = bf.tobytes()
            db.commit()

            print(f"Ingested {fname} as video_id={vm.video_id}")
    finally:
        db.close()


if __name__ == "__main__":
    # Adjust this path to your actual videos directory
    video_dir = os.path.join(PROJECT_ROOT, 'videos')
    if not os.path.isdir(video_dir):
        print(f"Error: folder not found: {video_dir}")
        sys.exit(1)

    ingest_folder(video_dir, user_id=1)
