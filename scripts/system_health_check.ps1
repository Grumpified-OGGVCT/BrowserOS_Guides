$ErrorActionPreference = "SilentlyContinue"

# CPU Load
$cpu = Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average | Select-Object -ExpandProperty Average

# RAM Usage
$os = Get-CimInstance Win32_OperatingSystem
$totalRam = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeRam = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$usedRam = [math]::Round($totalRam - $freeRam, 2)
$ramPercent = [math]::Round(($usedRam / $totalRam) * 100, 2)

# Disk Usage (C: Drive)
$disk = Get-PSDrive C | Select-Object @{Name="UsedGB";Expression={[math]::Round($_.Used/1GB,2)}}, @{Name="FreeGB";Expression={[math]::Round($_.Free/1GB,2)}}, @{Name="TotalGB";Expression={[math]::Round(($_.Used + $_.Free)/1GB,2)}}

# Port Status using .NET Sockets (Faster and Silent)
function Test-Port($port) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $result = $client.BeginConnect("localhost", $port, $null, $null)
        $success = $result.AsyncWaitHandle.WaitOne(200, $false)
        if ($success) {
            $client.EndConnect($result)
            $client.Close()
            return $true
        }
        return $false
    } catch {
        return $false
    }
}

$port3100 = Test-Port 3100
$port9000 = Test-Port 9000

# Construct JSON Object
$status = @{
    timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    cpu_load_percent = $cpu
    ram_usage = @{
        total_gb = $totalRam
        used_gb = $usedRam
        free_gb = $freeRam
        percent = $ramPercent
    }
    disk_c = $disk
    ports = @{
        mcp_server_3100 = if ($port3100) { "Listening" } else { "Closed" }
        cdp_9000 = if ($port9000) { "Listening" } else { "Closed" }
    }
    status = if ($port3100 -and $port9000) { "HEALTHY" } else { "DEGRADED" }
}

$status | ConvertTo-Json -Depth 3
