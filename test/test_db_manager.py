import pytest
import asyncio
from database.connections.db_manager import db_manager, initialize_databases, get_database_health

@pytest.mark.asyncio
async def test_initialize_and_health():
    # Khởi tạo
    await initialize_databases()
    # Kiểm tra health
    health = await get_database_health()
    assert health['postgres']['status'] == 'healthy'
    assert health['redis']['status'] == 'healthy'
    # Neo4j và LanceDB nếu sử dụng cũng healthy

    # Đóng kết nối
    await db_manager.close_all()