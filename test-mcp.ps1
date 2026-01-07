# Test MCP Endpoints
$serviceUrl = "https://open-meteo-mcp-874479064416.europe-west6.run.app"

Write-Host "Testing MCP Endpoints" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green
Write-Host ""

# Test 1: Health Check
Write-Host "1. Testing /mcp/health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$serviceUrl/mcp/health" -Method Get
    Write-Host "✅ Health: $($health.status)" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
}

# Test 2: Resources List
Write-Host "2. Testing resources/list..." -ForegroundColor Yellow
try {
    $body = @{
        jsonrpc = "2.0"
        id = 1
        method = "resources/list"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$serviceUrl/mcp" -Method Post -Headers @{"Content-Type"="application/json"} -Body $body
    Write-Host "✅ Resources found: $($response.result.resources.Count)" -ForegroundColor Green
    $response.result.resources | ForEach-Object { Write-Host "   - $($_.name)" }
    Write-Host ""
} catch {
    Write-Host "❌ Resources list failed: $_" -ForegroundColor Red
}

# Test 3: Prompts List
Write-Host "3. Testing prompts/list..." -ForegroundColor Yellow
try {
    $body = @{
        jsonrpc = "2.0"
        id = 2
        method = "prompts/list"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$serviceUrl/mcp" -Method Post -Headers @{"Content-Type"="application/json"} -Body $body
    Write-Host "✅ Prompts found: $($response.result.prompts.Count)" -ForegroundColor Green
    $response.result.prompts | ForEach-Object { Write-Host "   - $($_.name)" }
    Write-Host ""
} catch {
    Write-Host "❌ Prompts list failed: $_" -ForegroundColor Red
}

# Test 4: Tools List
Write-Host "4. Testing tools/list..." -ForegroundColor Yellow
try {
    $body = @{
        jsonrpc = "2.0"
        id = 3
        method = "tools/list"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$serviceUrl/mcp" -Method Post -Headers @{"Content-Type"="application/json"} -Body $body
    Write-Host "✅ Tools found: $($response.result.tools.Count)" -ForegroundColor Green
    $response.result.tools | ForEach-Object { Write-Host "   - $($_.name)" }
    Write-Host ""
} catch {
    Write-Host "❌ Tools list failed: $_" -ForegroundColor Red
}

Write-Host "Testing complete!" -ForegroundColor Green
