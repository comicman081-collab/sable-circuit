param([string]$Godot = 'D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64.exe')
$ErrorActionPreference = 'Stop'
$demoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if (-not (Test-Path -LiteralPath $Godot -PathType Leaf)) { throw 'Installed Godot executable not found; supply -Godot.' }
# The game is deliberately interactive. Helpers/tests use run_owned.py instead.
Start-Process -FilePath $Godot -ArgumentList @('--path', ('"' + $demoRoot + '"')) -WorkingDirectory $demoRoot -WindowStyle Normal
