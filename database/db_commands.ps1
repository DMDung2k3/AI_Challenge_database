# ==========================================
# DATABASE CONNECTION COMMANDS FOR WINDOWS
# ==========================================

# 1. CHECK IF DOCKER CONTAINERS ARE RUNNING
docker ps

# 2. CONNECT TO POSTGRESQL (correct syntax for PowerShell)
# Method 1: Direct connection with hardcoded values
docker exec -it ai_challenge_postgres psql -U ai_user -d ai_challenge

# Method 2: Using environment variables (if they exist)
docker exec -it ai_challenge_postgres psql -U ai_user -d ai_challenge -c "\dt"

# 3. CONNECT TO REDIS
# Method 1: Direct connection
docker exec -it ai_challenge_redis redis-cli ping

# Method 2: Connect to Redis CLI
docker exec -it ai_challenge_redis redis-cli

# 4. CONNECT TO NEO4J (check if it's running)
# Neo4j web interface: http://localhost:7474
# Username: neo4j, Password: ai_password
docker exec -it ai_challenge_neo4j cypher-shell -u neo4j -p ai_password

# 5. CHECK ELASTICSEARCH
docker exec -it ai_challenge_elasticsearch curl -X GET "localhost:9200/_cluster/health?pretty"

# 6. CHECK MINIO
# Web interface: http://localhost:9001
# Username: minioadmin, Password: minioadmin
docker exec -it ai_challenge_minio curl -I http://localhost:9000/minio/health/live

# ==========================================
# SPECIFIC POSTGRESQL COMMANDS
# ==========================================

# List all tables
docker exec -it ai_challenge_postgres psql -U ai_user -d ai_challenge -c "\dt"

# Describe a specific table
docker exec -it ai_challenge_postgres psql -U ai_user -d ai_challenge -c "\d+ video_metadata"

# Count records in a table
docker exec -it ai_challenge_postgres psql -U ai_user -d ai_challenge -c "SELECT COUNT(*) FROM video_metadata;"

# Check if pgvector extension is installed
docker exec -it ai_challenge_postgres psql -U ai_user -d ai_challenge -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# ==========================================
# SPECIFIC REDIS COMMANDS
# ==========================================

# Test Redis connection
docker exec -it ai_challenge_redis redis-cli ping

# Check Redis info
docker exec -it ai_challenge_redis redis-cli info

# List all keys
docker exec -it ai_challenge_redis redis-cli keys "*"

# Check Bloom filter
docker exec -it ai_challenge_redis redis-cli BF.INFO default_filter

# ==========================================
# TROUBLESHOOTING COMMANDS
# ==========================================

# Check container logs
docker logs ai_challenge_postgres
docker logs ai_challenge_redis
docker logs ai_challenge_neo4j
docker logs ai_challenge_elasticsearch
docker logs ai_challenge_minio

# Check container status
docker ps -a | findstr ai_challenge

# Restart containers if needed
docker restart ai_challenge_postgres
docker restart ai_challenge_redis

# Check network connectivity
docker network ls
docker network inspect ai_network

# ==========================================
# ALTERNATIVE: USE DOCKER COMPOSE
# ==========================================

# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs postgres
docker-compose logs redis

# ==========================================
# PYTHON SCRIPT TO TEST CONNECTIONS
# ==========================================

# Create a test script (save as test_connections.py)
# python test_connections.py
