import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from api.main import create_app
from database.connections.db_manager import initialize_databases, close_databases
from database.connections.metadata_db import get_session
from database.models.conversation import ConversationHistory
import pytest_asyncio
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create app instance
app = create_app()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest_asyncio.fixture(autouse=True, scope="session")
async def setup_and_teardown():
    """Setup and teardown for the entire test session"""
    try:
        logger.info("Initializing databases...")
        await initialize_databases()
        logger.info("Databases initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize databases: {e}")
        raise
    finally:
        logger.info("Cleaning up databases...")
        try:
            await close_databases()
            logger.info("Databases closed successfully")
        except Exception as e:
            logger.error(f"Error closing databases: {e}")

def test_app_routes():
    """Test to discover available routes"""
    with TestClient(app) as client:
        logger.info("Testing root endpoint...")
        response = client.get("/")
        logger.info(f"Root response: {response.status_code} - {response.json()}")
        assert response.status_code == 200
        
        # Try to discover health endpoint
        for health_path in ["/api/health", "/api/health/", "/health", "/health/"]:
            logger.info(f"Testing health endpoint: {health_path}")
            response = client.get(health_path)
            logger.info(f"Health response for {health_path}: {response.status_code}")
            if response.status_code == 200:
                logger.info(f"Health endpoint found at: {health_path}")
                logger.info(f"Health response: {response.json()}")
                break

def test_chat_endpoint_detailed():
    """Test chat endpoint with detailed logging"""
    with TestClient(app) as client:
        payload = {
            "session_id": "detailed_test_1",
            "message": "Detailed integration test",
            "metadata": {"source": "test"},
            "user_id": "user_detailed"
        }
        
        logger.info(f"Sending request to /api/chat/message with payload: {payload}")
        response = client.post("/api/chat/message", json=payload)
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        
        if response.status_code != 200:
            logger.error(f"Error response: {response.text}")
            # Try to get more details about the error
            try:
                error_data = response.json()
                logger.error(f"Error JSON: {error_data}")
            except:
                logger.error("Could not parse error response as JSON")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        logger.info(f"Response data: {data}")
        
        # Check response structure
        assert "status" in data, f"No status field in response: {data}"
        
        # Log all available fields
        logger.info(f"Available response fields: {list(data.keys())}")

def test_database_connection():
    """Test direct database connection"""
    try:
        logger.info("Testing direct database connection...")
        db = get_session()
        logger.info("Database session created successfully")
        
        # Try to query existing records
        try:
            all_records = db.query(ConversationHistory).all()
            logger.info(f"Found {len(all_records)} existing conversation records")
            
            # Log a few sample records if they exist
            for i, record in enumerate(all_records[:3]):
                logger.info(f"Record {i}: session_id={record.session_id}, message={record.user_message[:50]}...")
                
        except Exception as e:
            logger.error(f"Error querying conversation history: {e}")
            
        db.close()
        logger.info("Database connection test completed")
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def test_chat_and_db_integration():
    """Test chat endpoint and verify database integration"""
    with TestClient(app) as client:
        session_id = "integration_test_detailed"
        test_message = "Integration test with DB verification"
        
        payload = {
            "session_id": session_id,
            "message": test_message,
            "metadata": {"source": "test"},
            "user_id": "user_integration"
        }
        
        logger.info(f"Sending chat request with session_id: {session_id}")
        response = client.post("/api/chat/message", json=payload)
        
        assert response.status_code == 200, f"Chat request failed: {response.status_code} - {response.text}"
        
        data = response.json()
        logger.info(f"Chat response: {data}")
        
        # Wait a moment for database write to complete
        import time
        time.sleep(1)
        
        # Check database
        logger.info("Checking database for new record...")
        db = get_session()
        try:
            # Query all records for this session
            records = db.query(ConversationHistory).filter_by(session_id=session_id).all()
            logger.info(f"Found {len(records)} records for session_id: {session_id}")
            
            if len(records) == 0:
                # Check if there are any records at all
                all_records = db.query(ConversationHistory).all()
                logger.info(f"Total records in database: {len(all_records)}")
                
                # Check recent records
                recent_records = db.query(ConversationHistory).order_by(ConversationHistory.timestamp.desc()).limit(5).all()
                logger.info(f"Recent records: {len(recent_records)}")
                for record in recent_records:
                    logger.info(f"Recent record: session_id={record.session_id}, message={record.user_message[:50]}...")
            
            else:
                for record in records:
                    logger.info(f"Found record: session_id={record.session_id}, user_message={record.user_message}")
            
        except Exception as e:
            logger.error(f"Database query error: {e}")
            raise
        finally:
            db.close()

@pytest.mark.asyncio
async def test_async_chat_endpoint():
    """Test async chat endpoint"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        payload = {
            "session_id": "async_detailed_test",
            "message": "Async integration test",
            "metadata": {"source": "test"},
            "user_id": "user_async"
        }
        
        logger.info("Sending async request...")
        response = await client.post("/api/chat/message", json=payload)
        logger.info(f"Async response status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Async error response: {response.text}")
        
        assert response.status_code == 200
        
        data = response.json()
        logger.info(f"Async response data: {data}")

def test_api_routes_discovery():
    """Discover all available API routes"""
    with TestClient(app) as client:
        # Test various possible endpoints
        endpoints_to_test = [
            "/",
            "/api/",
            "/api/chat/",
            "/api/chat/message",
            "/api/health",
            "/api/health/",
            "/api/admin",
            "/api/admin/",
            "/api/upload",
            "/api/upload/",
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = client.get(endpoint)
                logger.info(f"Endpoint {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        logger.info(f"  Response: {data}")
                    except:
                        logger.info(f"  Response (text): {response.text[:100]}...")
            except Exception as e:
                logger.error(f"Error testing endpoint {endpoint}: {e}")