param(
  [string]$PythonExe = "C:\Python311\python.exe",
  [string]$ProjectDir = "C:\path\to\intelligent-adaptive-training-logic"
)
& $PythonExe "$ProjectDir\backend\backend_rotation.py"
