param(
  [string]$PythonExe = "C:\Python311\python.exe",
  [string]$ProjectDir = "C:\path\to\intelligent-adaptive-training-logic",
  [string]$TaskName = "AdaptiveRotationHourly"
)

$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "$ProjectDir\backend\backend_rotation.py"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Hourly rotation analysis"
Write-Host "Task '$TaskName' registered."
