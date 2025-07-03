# test/test_models.py

import os
import sys
import uuid
import pytest

# 1) Ensure project root is on sys.path
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from database.connections.metadata_db import get_engine
from database.models.video_metadata import VideoMetadata

@pytest.fixture(scope="module")
def session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    sess = Session()
    yield sess
    sess.close()

def test_video_insert_and_query(session):
    # 2) Tạo video_id ngẫu nhiên để không trùng key
    vid_id = f"test_vid_{uuid.uuid4().hex}"
    vid = VideoMetadata(
        video_id=vid_id,
        video_path="/tmp/test.mp4",
        filename="test.mp4"
    )

    # 3) Insert và commit
    session.add(vid)
    session.commit()

    # 4) Query lại theo video_id
    fetched = session.query(VideoMetadata).filter_by(video_id=vid_id).one()
    assert fetched.filename == "test.mp4"
    assert fetched.video_id == vid_id

    # 5) Cleanup: xóa khỏi DB để tránh dư thừa
    session.delete(fetched)
    session.commit()
