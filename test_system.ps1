# System Test Script for AI Challenge Database Infrastructure
# PowerShell version with proper syntax for Windows

Write-Host "=== AI Challenge Database System Test ===" -ForegroundColor Green

# Function to test HTTP endpoints
function Test-HttpEndpoint {
    param(
        [string]$Url,
        [string]$ServiceName,
        [hashtable]$Headers = @{},
        [string]$Method = "GET"
    )
    
    try {
        Write-Host "Testing $ServiceName at $Url..." -ForegroundColor Yellow
        if ($Headers.Count -gt 0) {
            $response = Invoke-WebRequest -Uri $Url -Method $Method -Headers $Headers -UseBasicParsing -TimeoutSec 10
        } else {
            $response = Invoke-WebRequest -Uri $Url -Method $Method -UseBasicParsing -TimeoutSec 10
        }
        Write-Host "✓ $ServiceName is healthy (Status: $($response.StatusCode))" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ $ServiceName failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to test database connection
function Test-DatabaseConnection {
    param(
        [string]$ContainerName,
        [string]$Command,
        [string]$ServiceName
    )
    
    try {
        Write-Host "Testing $ServiceName database connection..." -ForegroundColor Yellow
        $result = docker exec $ContainerName $Command
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $ServiceName database connection successful" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ $ServiceName database connection failed" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "✗ $ServiceName database test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

Write-Host "`n1. Checking container status..." -ForegroundColor Blue
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n2. Testing PostgreSQL + pgvector..." -ForegroundColor Blue
$pgTest = docker exec ai_challenge_postgres psql -U ai_user -d ai_challenge -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
if ($pgTest -match "vector") {
    Write-Host "✓ PostgreSQL with pgvector is working" -ForegroundColor Green
} else {
    Write-Host "✗ pgvector extension not found" -ForegroundColor Red
}

Write-Host "`n3. Testing Redis..." -ForegroundColor Blue
$redisTest = docker exec ai_challenge_redis redis-cli -a ai_password ping 2>$null
if ($redisTest -eq "PONG") {
    Write-Host "✓ Redis is working" -ForegroundColor Green
} else {
    Write-Host "✗ Redis connection failed" -ForegroundColor Red
}

Write-Host "`n4. Testing Neo4j..." -ForegroundColor Blue
Test-HttpEndpoint -Url "http://localhost:7474" -ServiceName "Neo4j Browser"

Write-Host "`n5. Testing LanceDB..." -ForegroundColor Blue
Test-HttpEndpoint -Url "http://localhost:8002/health" -ServiceName "LanceDB"

# Test LanceDB functionality
Write-Host "Testing LanceDB functionality..." -ForegroundColor Yellow
$lanceTest = docker exec ai_challenge_lancedb python -c "
import lancedb
try:
    db = lancedb.connect('/data/lancedb')
    tables = db.table_names()
    print(f'LanceDB tables: {tables}')
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
"
if ($lanceTest -match "SUCCESS") {
    Write-Host "✓ LanceDB functionality test passed" -ForegroundColor Green
} else {
    Write-Host "✗ LanceDB functionality test failed" -ForegroundColor Red
}

Write-Host "`n6. Testing MinIO..." -ForegroundColor Blue
Test-HttpEndpoint -Url "http://localhost:9000/minio/health/live" -ServiceName "MinIO API"
Test-HttpEndpoint -Url "http://localhost:9001" -ServiceName "MinIO Console"

Write-Host "`n7. Testing Prometheus..." -ForegroundColor Blue
Test-HttpEndpoint -Url "http://localhost:9090/-/healthy" -ServiceName "Prometheus Health"
Test-HttpEndpoint -Url "http://localhost:9090/graph" -ServiceName "Prometheus UI"

Write-Host "`n8. Testing Grafana..." -ForegroundColor Blue
Test-HttpEndpoint -Url "http://localhost:3001/api/health" -ServiceName "Grafana Health"

# Test Grafana login
Write-Host "Testing Grafana authentication..." -ForegroundColor Yellow
$grafanaAuth = @{
    'Authorization' = 'Basic ' + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes('admin:admin'))
}
Test-HttpEndpoint -Url "http://localhost:3001/api/datasources" -ServiceName "Grafana API" -Headers $grafanaAuth

Write-Host "`n9. Testing network connectivity..." -ForegroundColor Blue
$networkTest = docker network inspect ai_network 2>$null
if ($networkTest) {
    Write-Host "✓ ai_network exists and is configured" -ForegroundColor Green
    
    # Test inter-container communication
    Write-Host "Testing inter-container communication..." -ForegroundColor Yellow
    $pingTest = docker exec ai_challenge_postgres sh -c "apt-get update -qq && apt-get install -y iputils-ping -qq && ping -c 2 ai_challenge_redis" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Inter-container communication working" -ForegroundColor Green
    } else {
        Write-Host "✗ Inter-container communication failed" -ForegroundColor Red
    }
} else {
    Write-Host "✗ ai_network not found" -ForegroundColor Red
}

Write-Host "`n10. Resource usage summary..." -ForegroundColor Blue
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

Write-Host "`n=== Test Summary ===" -ForegroundColor Green
Write-Host "Database infrastructure test completed!" -ForegroundColor Cyan
Write-Host "Services should be accessible at:" -ForegroundColor White
Write-Host "- PostgreSQL: localhost:5432" -ForegroundColor Gray
Write-Host "- Redis: localhost:6379" -ForegroundColor Gray  
Write-Host "- Neo4j Browser: http://localhost:7474" -ForegroundColor Gray
Write-Host "- Neo4j Bolt: bolt://localhost:7687" -ForegroundColor Gray
Write-Host "- LanceDB: localhost:8002" -ForegroundColor Gray
Write-Host "- MinIO API: http://localhost:9000" -ForegroundColor Gray
Write-Host "- MinIO Console: http://localhost:9001" -ForegroundColor Gray
Write-Host "- Prometheus: http://localhost:9090" -ForegroundColor Gray
Write-Host "- Grafana: http://localhost:3001 (admin/admin)" -ForegroundColor Gray