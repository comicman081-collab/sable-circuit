[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$outputDir = Join-Path $projectRoot 'artifacts\aster_move_aim_runtime_acceptance'
$godot = 'D:\AI 종합 폴더\Godot\4.7.1-standard\Godot_v4.7.1-stable_win64_console.exe'
$python = 'C:\Users\AAA\AppData\Local\Programs\Python\Python311\python.exe'
$rawAvi = Join-Path $outputDir 'ASTER_MOVE_AIM_RUNTIME_ACCEPTANCE_RAW.avi'
$currentMp4 = Join-Path $outputDir 'ASTER_MOVE_AIM_RUNTIME_ACCEPTANCE.mp4'
$previousMp4 = Join-Path $outputDir 'ASTER_MOVE_AIM_RUNTIME_ACCEPTANCE_PREV.mp4'
$transcoder = Join-Path $projectRoot 'tools\art_pipeline\transcode_aster_acceptance_video.py'
$resolutionValidator = Join-Path $projectRoot 'tools\art_pipeline\validate_visual_evidence_1080p.py'
$resolutionReport = Join-Path $outputDir 'ASTER_MOVE_AIM_RUNTIME_1080P_QA.json'

if (-not (Test-Path -LiteralPath $godot -PathType Leaf)) { throw "Godot missing: $godot" }
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw "Python missing: $python" }
if (-not (Test-Path -LiteralPath $transcoder -PathType Leaf)) { throw "Transcoder missing: $transcoder" }
if (-not (Test-Path -LiteralPath $resolutionValidator -PathType Leaf)) { throw "1080p validator missing: $resolutionValidator" }

New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
$resolvedOutput = (Resolve-Path -LiteralPath $outputDir).Path
if (-not $resolvedOutput.StartsWith($projectRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Output escaped project root: $resolvedOutput"
}

# The user-requested retention rule is current + exactly one previous review
# video.  These are explicit files inside the verified output directory; no
# wildcard or recursive deletion is used.
if (Test-Path -LiteralPath $previousMp4 -PathType Leaf) {
    Remove-Item -LiteralPath $previousMp4 -Force
}
if (Test-Path -LiteralPath $currentMp4 -PathType Leaf) {
    Move-Item -LiteralPath $currentMp4 -Destination $previousMp4
}
if (Test-Path -LiteralPath $rawAvi -PathType Leaf) {
    Remove-Item -LiteralPath $rawAvi -Force
}

$arguments = @(
    '--path', $projectRoot,
    '--display-driver', 'windows',
    '--rendering-method', 'gl_compatibility',
    '--rendering-driver', 'opengl3',
    '--fixed-fps', '30',
    '--disable-vsync',
    '--write-movie', $rawAvi,
    '--script', 'res://tests/render/aster_move_aim_runtime_acceptance_capture.gd'
)
$process = Start-Process -FilePath $godot -ArgumentList $arguments -WindowStyle Hidden -Wait -PassThru
if ($process.ExitCode -ne 0) { throw "Godot acceptance capture failed with exit code $($process.ExitCode)" }
if (-not (Test-Path -LiteralPath $rawAvi -PathType Leaf)) { throw "Godot did not create the AVI" }

& $python $transcoder $rawAvi $currentMp4
if ($LASTEXITCODE -ne 0) { throw "MP4 transcode/verification failed" }
if (-not (Test-Path -LiteralPath $currentMp4 -PathType Leaf)) { throw "Verified MP4 missing" }

$reviewEvidence = @($currentMp4)
$reviewEvidence += Get-ChildItem -LiteralPath $outputDir -Filter '*.png' -File | ForEach-Object { $_.FullName }
if ($reviewEvidence.Count -lt 4) { throw "Expected runtime video and native review PNG evidence" }
& $python $resolutionValidator @reviewEvidence --output $resolutionReport
if ($LASTEXITCODE -ne 0) { throw "Global native 1080p visual-evidence gate failed" }

# The compact MP4 is now independently decodable, so the large intermediate is
# no longer a review candidate and can be removed without risking the result.
Remove-Item -LiteralPath $rawAvi -Force
Write-Output "ASTER_MOVE_AIM_RUNTIME_ACCEPTANCE_CAPTURE: PASS"
Write-Output $currentMp4
