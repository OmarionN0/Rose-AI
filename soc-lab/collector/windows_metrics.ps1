# Read-only Windows aggregate metrics collector. No process names, IPs or usernames.
param([int]$IntervalSeconds = 30, [switch]$Once)
$ErrorActionPreference = 'Stop'
if ($IntervalSeconds -lt 5) { throw 'IntervalSeconds must be >= 5' }
$token = $env:ROSE_SOC_TOKEN
if ([string]::IsNullOrWhiteSpace($token) -or $token.Length -lt 32) { throw 'Set ROSE_SOC_TOKEN in this Windows PowerShell session first.' }
$endpoint = 'http://127.0.0.1:8000/events'
while ($true) {
    try {
        $cpu = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
        $os = Get-CimInstance Win32_OperatingSystem
        $total = [double]$os.TotalVisibleMemorySize
        $free = [double]$os.FreePhysicalMemory
        $ram = if ($total -gt 0) { [math]::Round(100 * (1 - $free / $total), 1) } else { 0 }
        $payload = @{source='windows-readonly-metrics';host='Windows';event_type='system_metrics';details=@{cpu_percent=[math]::Round([double]$cpu,1);memory_percent=$ram}} | ConvertTo-Json -Depth 4 -Compress
        Invoke-RestMethod -Method Post -Uri $endpoint -Headers @{Authorization="Bearer $token"} -ContentType 'application/json' -Body $payload | Out-Null
        Write-Host 'Windows aggregate metrics submitted'
    } catch {
        Write-Warning 'Unable to submit local metrics; check API and authentication.'
    }
    if ($Once) { break }
    Start-Sleep -Seconds $IntervalSeconds
}
