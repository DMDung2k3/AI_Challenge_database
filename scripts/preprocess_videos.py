#!/usr/bin/env python3
# scripts/preprocessing_videos.py

import os, sys
# ── path hack ──
this_dir    = os.path.dirname(__file__)
project_dir = os.path.abspath(os.path.join(this_dir, ".."))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

import argparse
import logging
from datetime import datetime
import ffmpeg

from database.connections.metadata_db import MetadataDB
from database.models.video_metadata    import VideoMetadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

metadb = MetadataDB()

def extract_keyframes(video_path: str, output_dir: str) -> int:
    os.makedirs(output_dir, exist_ok=True)
    (
        ffmpeg
        .input(video_path)
        .filter("select", "eq(pict_type\\,I)")
        .output(os.path.join(output_dir, "frame_%04d.jpg"), vsync=0)
        .run(quiet=True, overwrite_output=True)
    )
    return len(os.listdir(output_dir))

def process_videos(input_dir: str, keyframe_dir: str):
    session = metadb.get_session()
    for fn in os.listdir(input_dir):
        if not fn.lower().endswith((".mp4", ".mov", ".avi")):
            continue
        path = os.path.join(input_dir, fn)
        vid  = os.path.splitext(fn)[0]
        logger.info("Processing %s", path)

        vm = session.query(VideoMetadata).filter_by(video_id=vid).first()
        if not vm:
            vm = VideoMetadata(video_id=vid, video_path=path, filename=fn)
            session.add(vm)
        vm.processing_status = "processing"
        vm.processing_started_at = datetime.utcnow()
        session.commit()

        out = os.path.join(keyframe_dir, vid)
        count = extract_keyframes(path, out)
        logger.info("Extracted %d keyframes for %s", count, vid)

        vm.keyframes_extracted = count
        vm.processing_status = "completed"
        vm.processing_completed_at = datetime.utcnow()
        session.commit()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir",    required=True)
    p.add_argument("--keyframe-dir", required=True)
    args = p.parse_args()
    process_videos(args.input_dir, args.keyframe_dir)
    logger.info("Done.")
