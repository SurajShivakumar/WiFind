# Test GPS Endpoint
$body = @{
    lat = 47.6062
    lon = -122.3321
    acc = 10
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/gps" -Method POST -Body $body -ContentType "application/json"
    Write-Host "✅ GPS endpoint working!" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}
