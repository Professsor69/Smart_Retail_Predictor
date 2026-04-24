# ============================================
# Smart Retail Predictor - Stop Server Script
# Double-click or run: .\stop_server.ps1
# ============================================

Write-Host "🔍 Looking for server on port 8000..." -ForegroundColor Cyan

$connections = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

if ($connections) {
    $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique

    foreach ($pid in $pids) {
        if ($pid -eq 0) { continue }

        $proc = Get-CimInstance Win32_Process -Filter "ProcessId = $pid" -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "⚡ Killing: $($proc.Name) (PID $pid)" -ForegroundColor Yellow
            taskkill /PID $pid /F /T 2>&1 | Out-Null
        } else {
            # Try killing child processes if parent is a ghost
            $children = Get-CimInstance Win32_Process -Filter "ParentProcessId = $pid" -ErrorAction SilentlyContinue
            foreach ($child in $children) {
                Write-Host "⚡ Killing child: $($child.Name) (PID $($child.ProcessId))" -ForegroundColor Yellow
                taskkill /PID $($child.ProcessId) /F /T 2>&1 | Out-Null
            }
        }
    }

    # Also kill any lingering Python processes running uvicorn
    $pythonProcs = Get-Process -Name "python*" -ErrorAction SilentlyContinue
    foreach ($p in $pythonProcs) {
        $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId = $($p.Id)").CommandLine
        if ($cmd -like "*uvicorn*" -or $cmd -like "*main*" -or $cmd -like "*fastapi*") {
            Write-Host "⚡ Killing uvicorn Python process (PID $($p.Id))" -ForegroundColor Yellow
            Stop-Process -Id $p.Id -Force
        }
    }

    Start-Sleep -Seconds 1
    $check = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
    if ($check) {
        Write-Host "❌ Port 8000 still in use. Try running this script as Administrator." -ForegroundColor Red
    } else {
        Write-Host "✅ Server stopped! Port 8000 is now free." -ForegroundColor Green
    }

} else {
    Write-Host "✅ No server found on port 8000. It's already stopped!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
