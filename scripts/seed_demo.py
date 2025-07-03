# scripts/seed_demo.py
import os, sys
from sqlalchemy import text
# ensure project-root
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.connections import get_engine
from database.models.base import Base
from database.models.video_metadata import VideoMetadata
from database.models.user_session import UserSession
from datetime import datetime
import uuid

engine = get_engine()
# 1) Tạo bảng (nếu chưa) – nhưng migrations đã tạo rồi
Base.metadata.create_all(engine)

# 2) Chèn 1 video metadata demo
with engine.begin() as conn:
    conn.execute(text("""
        INSERT INTO video_metadata (id, video_id, video_path, filename, uploaded_at)
        VALUES (:id, :vid, :path, :fn, :ts)
        ON CONFLICT (video_id) DO NOTHING
    """), {
        "id": str(uuid.uuid4()),
        "vid": "demo_video_1",
        "path": "/videos/demo.mp4",
        "fn": "demo.mp4",
        "ts": datetime.utcnow()
    })

    # 3) Chèn 1 user session demo
    conn.execute(text("""
        INSERT INTO user_sessions (id, session_id, user_id, start_time, last_activity)
        VALUES (:id, :sid, :uid, :ts, :ts)
        ON CONFLICT (session_id) DO NOTHING
    """), {
        "id": str(uuid.uuid4()),
        "sid": "demo_session_1",
        "uid": "demo_user",
        "ts": datetime.utcnow()
    })
print("✅ Seed demo data hoàn tất.")
