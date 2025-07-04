# api/services/video_service.py (hoặc trong orchestrator)

from bloom_filter2 import BloomFilter
from database.connections.metadata_db import SessionLocal
from database.models.video_metadata import VideoMetadata

def search_videos_by_bloom(prompt: str, top_k: int = 5):
    # 1) Build BF cho prompt
    bf_prompt = BloomFilter.from_bytes(prompt.encode(), max_elements=10000, error_rate=0.01)
    db = SessionLocal()
    candidates = []
    # 2) Lấy tất cả video bloom data
    for vm in db.query(VideoMetadata.video_id, VideoMetadata.bloom_filter).all():
        video_id, bf_bytes = vm
        bf_video = BloomFilter.from_bytes(bf_bytes)
        # 3) Tính điểm: số token prompt có trong video BF
        score = sum(1 for token in prompt.split() if token.lower() in bf_video)
        candidates.append((video_id, score))
    db.close()
    # 4) Chọn top_k
    candidates.sort(key=lambda x: x[1], reverse=True)
    return [{"video_id": vid, "score": sc} for vid, sc in candidates[:top_k]]
