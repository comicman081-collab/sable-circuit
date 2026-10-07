<#
Historical ASTER Static Master source pipeline. RETIRED: do not invoke.

There is no graphical Blender, Computer Use, Photoshop, cloud inference, or
Krea path in this script.  Blender is invoked only with --background.  Qwen
uses the local ComfyUI runtime read-only, while every generated input, output,
temporary directory, and log remains below this project.

`Validate` is intentionally the default.  `Author` creates exactly one new
candidate ID and still leaves it at USER_REVIEW_REQUIRED; it never starts
animation, runtime integration, or unit expansion. The active 2026-08-30
production lock disables both modes below so this file remains provenance only.
#>

[CmdletBinding()]
param(
    [ValidateSet('Validate', 'Author')]
    [string]$Mode = 'Validate',
    [ValidatePattern('^[a-z0-9][a-z0-9_-]{2,80}$')]
    [string]$CandidateId = 'qwen_static_master_fullmass_v3_seed251114',
    [int]$Seed = 251114,
    [ValidateRange(8, 64)]
    [int]$Steps = 32,
    [string]$QwenRuntime = $(if ($env:SABLE_QWEN_2511_RUNTIME) { $env:SABLE_QWEN_2511_RUNTIME } else { 'C:\AI_ENVS\ComfyUI_windows_portable\SableQwen2511' }),
    [string]$QwenPython = $(if ($env:SABLE_QWEN_2511_PYTHON) { $env:SABLE_QWEN_2511_PYTHON } else { 'C:\AI_ENVS\ComfyUI_windows_portable\python_embeded\python.exe' }),
    [string]$ModelRoot = $(if ($env:SABLE_CIRCUIT_MODEL_ROOT) { $env:SABLE_CIRCUIT_MODEL_ROOT } else { 'C:\AI_MODELS' }),
    [string]$Blender = 'tools\blender\5.2.1\blender.exe'
)

throw 'RETIRED_PIPELINE: ASTER Qwen/ComfyUI Static Master authoring is disabled; use the active Fire16 repair contract.'

$ErrorActionPreference = 'Stop'
$projectRoot = [System.IO.Path]::GetFullPath((Split-Path -Parent (Split-Path -Parent $PSScriptRoot)))
$qwenEdits = Join-Path $projectRoot 'art_src\pilot_v2\aster_v2\qwen_edits'
$guideParent = Join-Path $projectRoot 'art_src\pilot_v2\aster_v2\pose_guides\_aster_static_master_pipeline'
$candidateRoot = Join-Path $qwenEdits $CandidateId
$guideRoot = Join-Path $guideParent $CandidateId
$pythonTool = Join-Path $projectRoot 'tools\qwen_image_edit_2511\run_aster_static_master_qwen_candidate.py'
$matteTool = Join-Path $projectRoot 'tools\art_pipeline\apply_green_matte.py'
$finalizeTool = Join-Path $projectRoot 'tools\art_pipeline\finalize_aster_static_master_candidate.py'
$validateTool = Join-Path $projectRoot 'tools\art_pipeline\validate_aster_static_master_candidate.py'
$previewTool = Join-Path $projectRoot 'art_src\pilot_v2\blender\build_aster_static_master_fullmass_v3_preview.py'
$guideBuilder = Join-Path $projectRoot 'art_src\pilot_v2\blender\create_aster_fullmass_structure_guide_v1.py'
$reference = Join-Path $projectRoot 'art_src\pilot_v2\aster_v2\static_master\ASTER_STATIC_MASTER_AUTHORITY\02_image_a_render_reference.png'
$licenseInventory = Join-Path $projectRoot 'tools\licenses\qwen_image_edit_2511\MODEL_INVENTORY.json'

function Assert-ProjectPath([string]$PathValue, [string]$Label) {
    $resolved = [System.IO.Path]::GetFullPath($PathValue)
    $relative = [System.IO.Path]::GetRelativePath($projectRoot, $resolved)
    if ($relative -eq '..' -or $relative.StartsWith("..$([System.IO.Path]::DirectorySeparatorChar)")) {
        throw "$Label must remain inside project: $resolved"
    }
    return $resolved
}

function Assert-ReadOnlyExternalPath([string]$PathValue, [string]$Label) {
    $resolved = [System.IO.Path]::GetFullPath($PathValue)
    if ($resolved -notmatch '^[A-Za-z]:\\') { throw "$Label must be a resolved local path: $resolved" }
    if ($resolved -match '(?i)krea') { throw "$Label must not reference Krea: $resolved" }
    if (-not (Test-Path -LiteralPath $resolved)) { throw "$Label is unavailable: $resolved" }
    return $resolved
}

function Quote-Argument([string]$Value) {
    return '"' + $Value.Replace('"', '\"') + '"'
}

function Wait-ForQwenServer {
    param([int]$TimeoutSeconds = 90)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        try {
            $response = Invoke-RestMethod -Uri 'http://127.0.0.1:8190/system_stats' -Method Get -TimeoutSec 4
            if ($null -ne $response) { return }
        } catch {
            Start-Sleep -Milliseconds 750
        }
    } while ((Get-Date) -lt $deadline)
    throw 'Timed out waiting for isolated local Qwen ComfyUI on loopback port 8190.'
}

function Assert-PortUnused {
    $listener = Get-NetTCPConnection -LocalPort 8190 -State Listen -ErrorAction SilentlyContinue
    if ($listener) { throw 'Port 8190 is already in use. The pipeline will not attach to or stop an unknown process.' }
}

$candidateRoot = Assert-ProjectPath $candidateRoot 'candidate root'
$guideRoot = Assert-ProjectPath $guideRoot 'guide root'
$qwenRuntimeResolved = Assert-ReadOnlyExternalPath $QwenRuntime 'Qwen runtime'
$qwenPythonResolved = Assert-ReadOnlyExternalPath $QwenPython 'Qwen Python'
$modelRootResolved = Assert-ReadOnlyExternalPath $ModelRoot 'local model root'
$blenderResolved = Assert-ProjectPath (Join-Path $projectRoot $Blender) 'Blender executable'
foreach ($required in @($pythonTool, $matteTool, $finalizeTool, $validateTool, $previewTool, $guideBuilder, $reference, $blenderResolved)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "required pipeline file is unavailable: $required" }
}
if (-not (Test-Path -LiteralPath $licenseInventory -PathType Leaf)) { throw "Qwen license inventory is unavailable: $licenseInventory" }
try {
    $inventory = Get-Content -LiteralPath $licenseInventory -Raw | ConvertFrom-Json
} catch {
    throw "Qwen license inventory is invalid JSON: $licenseInventory"
}
if ($inventory.krea2_used -ne $false -or $inventory.paid_or_noncommercial_models_used -ne $false) {
    throw 'Qwen license inventory does not meet the SABLE commercial-use policy.'
}
if (Test-Path -LiteralPath (Join-Path $qwenRuntimeResolved 'ComfyUI\extra_model_paths.yaml')) {
    throw 'Refusing a Qwen runtime with extra_model_paths.yaml: the SABLE path must stay isolated from Krea or other registries.'
}
foreach ($expected in $inventory.weights) {
    if ($expected.license -ne 'apache-2.0' -or $expected.commercial_use -ne $true -or $expected.local_inference_allowed -ne $true) {
        throw "Qwen inventory license rejects $($expected.filename)"
    }
    $modelPath = switch ($expected.kind) {
        'diffusion' { Join-Path $qwenRuntimeResolved "models\diffusion_models\$($expected.filename)"; break }
        'text_encoder' { Join-Path $qwenRuntimeResolved "models\text_encoders\$($expected.filename)"; break }
        'vae' { Join-Path $qwenRuntimeResolved "models\vae\$($expected.filename)"; break }
        default { throw "unexpected Qwen inventory component: $($expected.kind)" }
    }
    if (-not (Test-Path -LiteralPath $modelPath -PathType Leaf)) { throw "approved local Qwen weight is unavailable: $modelPath" }
    if ((Get-Item -LiteralPath $modelPath).Length -ne [Int64]$expected.file_size) {
        throw "Qwen weight size differs from the pinned inventory: $modelPath"
    }
}

if ($Mode -eq 'Validate') {
    $oldNoBytecode = $env:PYTHONDONTWRITEBYTECODE
    try {
        $env:PYTHONDONTWRITEBYTECODE = '1'
        & $qwenPythonResolved $validateTool --candidate-root $candidateRoot
        if ($LASTEXITCODE -ne 0) { throw "technical candidate validation failed with exit code $LASTEXITCODE" }
        Write-Output "ASTER_STATIC_MASTER_PIPELINE=VALIDATED; gate=USER_REVIEW_REQUIRED; expansion=HOLD"
    }
    finally {
        $env:PYTHONDONTWRITEBYTECODE = $oldNoBytecode
    }
    exit 0
}

if ((Test-Path -LiteralPath $candidateRoot) -or (Test-Path -LiteralPath $guideRoot)) {
    throw "Author refuses to overwrite an existing candidate or guide ID: $CandidateId"
}

$workspace = Join-Path $candidateRoot '_comfy_workspace'
$serverProcess = $null
$success = $false
$oldRuntime = $env:SABLE_QWEN_2511_RUNTIME
$oldModelRoot = $env:SABLE_CIRCUIT_MODEL_ROOT
$oldNoBytecode = $env:PYTHONDONTWRITEBYTECODE
try {
    $env:PYTHONDONTWRITEBYTECODE = '1'
    New-Item -ItemType Directory -Path $candidateRoot -Force | Out-Null
    # Headless only. This guide is a spatial control and is explicitly not a final body asset.
    & $blenderResolved --background --python $guideBuilder -- --output $guideRoot --resolution 1024
    if ($LASTEXITCODE -ne 0) { throw "headless Blender guide build failed with exit code $LASTEXITCODE" }
    $guideImage = Join-Path $guideRoot 'ASTER_SM_FULLMASS_STRUCTURE_GUIDE_GREEN.png'
    if (-not (Test-Path -LiteralPath $guideImage -PathType Leaf)) { throw 'headless Blender guide image was not produced' }

    Assert-PortUnused
    $comfyEntry = Join-Path $qwenRuntimeResolved 'ComfyUI\main.py'
    $models = Join-Path $qwenRuntimeResolved 'models'
    $logRoot = Join-Path $workspace 'logs'
    foreach ($directory in @($workspace, $logRoot, (Join-Path $workspace 'input'), (Join-Path $workspace 'output'), (Join-Path $workspace 'temp'), (Join-Path $workspace 'user'))) {
        New-Item -ItemType Directory -Path (Assert-ProjectPath $directory 'Comfy workspace directory') -Force | Out-Null
    }
    $arguments = @(
        (Quote-Argument $comfyEntry), '--base-directory', (Quote-Argument (Join-Path $qwenRuntimeResolved 'ComfyUI')),
        '--models-directory', (Quote-Argument $models), '--listen', '127.0.0.1', '--port', '8190', '--disable-auto-launch',
        '--input-directory', (Quote-Argument (Join-Path $workspace 'input')),
        '--output-directory', (Quote-Argument (Join-Path $workspace 'output')),
        '--temp-directory', (Quote-Argument (Join-Path $workspace 'temp')),
        '--user-directory', (Quote-Argument (Join-Path $workspace 'user'))
    ) -join ' '
    $serverProcess = Start-Process -FilePath $qwenPythonResolved -ArgumentList $arguments -PassThru -WindowStyle Hidden `
        -WorkingDirectory $projectRoot -RedirectStandardOutput (Join-Path $logRoot 'comfy_stdout.log') `
        -RedirectStandardError (Join-Path $logRoot 'comfy_stderr.log')
    Wait-ForQwenServer

    $env:SABLE_QWEN_2511_RUNTIME = $qwenRuntimeResolved
    $env:SABLE_CIRCUIT_MODEL_ROOT = $modelRootResolved
    & $qwenPythonResolved $pythonTool --output $candidateRoot --guide $guideImage --workspace $workspace --seed $Seed --steps $Steps
    if ($LASTEXITCODE -ne 0) { throw "local Qwen candidate authoring failed with exit code $LASTEXITCODE" }
    & $qwenPythonResolved $matteTool aster --input (Join-Path $candidateRoot 'candidate\ASTER_STATIC_MASTER_QWEN_RAW.png') `
        --output (Join-Path $candidateRoot 'candidate\ASTER_STATIC_MASTER_QWEN_GREEN.png') `
        --mask (Join-Path $candidateRoot 'candidate\ASTER_STATIC_MASTER_QWEN_MASK.png') `
        --qa (Join-Path $candidateRoot 'candidate\ASTER_STATIC_MASTER_QWEN_GREEN_QA.json') --seed $Seed
    if ($LASTEXITCODE -ne 0) { throw "exact-green matte stage failed with exit code $LASTEXITCODE" }
    & $qwenPythonResolved $previewTool --candidate-root $candidateRoot --prefix ASTER_STATIC_MASTER
    if ($LASTEXITCODE -ne 0) { throw "review preview build failed with exit code $LASTEXITCODE" }
    & $qwenPythonResolved $finalizeTool --candidate-root $candidateRoot --guide $guideImage --purge-intermediates
    if ($LASTEXITCODE -ne 0) { throw "candidate finalization failed with exit code $LASTEXITCODE" }
    & $qwenPythonResolved $validateTool --candidate-root $candidateRoot
    if ($LASTEXITCODE -ne 0) { throw "candidate technical validation failed with exit code $LASTEXITCODE" }
    $success = $true
    Write-Output "ASTER_STATIC_MASTER_PIPELINE=AUTHORED; gate=USER_REVIEW_REQUIRED; expansion=HOLD"
}
finally {
    if ($serverProcess -and -not $serverProcess.HasExited) { Stop-Process -Id $serverProcess.Id -Force }
    $env:SABLE_QWEN_2511_RUNTIME = $oldRuntime
    $env:SABLE_CIRCUIT_MODEL_ROOT = $oldModelRoot
    $env:PYTHONDONTWRITEBYTECODE = $oldNoBytecode
    if (-not $success) {
        # This exact new candidate and its exact matching temporary guide are
        # the only cleanup targets; no external local-model source is writable.
        foreach ($target in @($candidateRoot, $guideRoot)) {
            $checked = Assert-ProjectPath $target 'failed candidate cleanup target'
            if (Test-Path -LiteralPath $checked) { Remove-Item -LiteralPath $checked -Recurse -Force }
        }
    }
}
