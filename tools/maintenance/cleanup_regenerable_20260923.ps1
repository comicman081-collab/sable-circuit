param(
    [switch]$Execute,
    [ValidateSet('staging', 'bytecode')][string]$Scope = 'staging'
)

$ErrorActionPreference = 'Stop'
$project = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path).TrimEnd('\')
$expected = [IO.Path]::GetFullPath('D:\AI 종합 폴더\Games\Sable-circuit').TrimEnd('\')
if (-not [string]::Equals($project, $expected, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Unexpected project root: $project"
}

$stage = Join-Path $project '.cache/sites_godot'
$capture = Join-Path $project 'cache/motion_lab_capture'
$smoke = Join-Path $project 'cache/motion_lab_smoke'
$temporary = Join-Path $project '.tmp'
$targets = if ($Scope -eq 'staging') { @($stage, $capture, $smoke) } else { @() }
$cleanupDirectories = @()
if ($Scope -eq 'staging') { $cleanupDirectories = @($stage, $capture, $smoke, $temporary) }
$projectPrefix = $project + [IO.Path]::DirectorySeparatorChar

function Assert-ProjectPath([string]$path) {
    $full = [IO.Path]::GetFullPath($path)
    if (-not $full.StartsWith($projectPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path escaped project: $full"
    }
    if ($full -eq $project) { throw 'Project root cannot be deleted' }
}

function Assert-NoReparse([string]$path) {
    if ((Get-Item -LiteralPath $path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw "Reparse point in cleanup scope: $path"
    }
}

foreach ($target in $cleanupDirectories) {
    Assert-ProjectPath $target
    if (Test-Path -LiteralPath $target) {
        Assert-NoReparse $target
        foreach ($entry in (Get-ChildItem -LiteralPath $target -Force -Recurse)) {
            Assert-ProjectPath $entry.FullName
            Assert-NoReparse $entry.FullName
        }
    }
}

$files = [Collections.Generic.List[IO.FileInfo]]::new()
foreach ($target in $targets) {
    if (-not (Test-Path -LiteralPath $target)) { continue }
    foreach ($file in (Get-ChildItem -LiteralPath $target -Force -Recurse -File)) {
        $relative = $file.FullName.Substring($projectPrefix.Length).Replace('\', '/')
        # Audio sources, audio manifests and original-sound intro video survive even in staging.
        if ($relative -match '^\.cache/sites_godot/(sound/|assets/audio/)' -or
            $relative -match '\.(wav|mp3|ogg|flac|aac|m4a|opus|wma|mid|midi|ogv|mp4|mkv|avi)(\.import)?$') {
            continue
        }
        $files.Add($file)
    }
}
if ($Scope -eq 'bytecode') {
    foreach ($relative in @(rg --files -uu -g '*.pyc' -g '*.pyo')) {
        $file = Get-Item -LiteralPath (Join-Path $project $relative) -Force
        Assert-ProjectPath $file.FullName
        Assert-NoReparse $file.FullName
        $files.Add($file)
    }
}

$rows = foreach ($file in $files) {
    [ordered]@{
        path = $file.FullName.Substring($projectPrefix.Length).Replace('\', '/')
        bytes = $file.Length
        sha256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}
$total = [long]0
foreach ($row in $rows) { $total += [long]$row.bytes }
$manifest = [ordered]@{
    batch = "regenerable_${Scope}_20260923"
    project = $project
    scope = if ($Scope -eq 'staging') { 'Generated Sites build staging except sound and sound-bearing media; September 11 temporary logs; empty temp directories.' } else { 'Regenerable Python bytecode (*.pyc, *.pyo) only.' }
    active_delivery_preserved = 'web_demo/dist'
    sound_preserved = $true
    files = @($rows)
    file_count = $files.Count
    bytes = $total
    status = if ($Execute) { 'planned' } else { 'dry_run' }
}
$manifestName = if ($Scope -eq 'staging') { 'regenerable_cache_retirement.json' } else { 'regenerable_bytecode_retirement.json' }
$manifestPath = Join-Path $project "qa/asset_cleanup_20260923/$manifestName"
if ($Execute) {
    if (Test-Path -LiteralPath $manifestPath) {
        throw "Retirement manifest already exists; do not overwrite its original hashes: $manifestPath"
    }
    $manifestDirectory = Split-Path -Parent $manifestPath
    [IO.Directory]::CreateDirectory($manifestDirectory) | Out-Null
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding utf8
    foreach ($file in $files) {
        Assert-ProjectPath $file.FullName
        Assert-NoReparse $file.FullName
        [IO.File]::Delete($file.FullName)
    }
    foreach ($target in $cleanupDirectories) {
        if (-not (Test-Path -LiteralPath $target)) { continue }
        $directories = @(Get-ChildItem -LiteralPath $target -Recurse -Force -Directory | Sort-Object { $_.FullName.Length } -Descending)
        foreach ($directory in @($directories + (Get-Item -LiteralPath $target -Force))) {
            Assert-ProjectPath $directory.FullName
            Assert-NoReparse $directory.FullName
            if (@(Get-ChildItem -LiteralPath $directory.FullName -Force).Count -eq 0) {
                [IO.Directory]::Delete($directory.FullName, $false)
            }
        }
    }
    if ($Scope -eq 'bytecode') {
        $parents = @($files | ForEach-Object { $_.DirectoryName } | Select-Object -Unique | Sort-Object Length -Descending)
        foreach ($parent in $parents) {
            if ((Split-Path -Leaf $parent) -ne '__pycache__') { continue }
            Assert-ProjectPath $parent
            Assert-NoReparse $parent
            if (@(Get-ChildItem -LiteralPath $parent -Force).Count -eq 0) {
                [IO.Directory]::Delete($parent, $false)
            }
        }
    }
    $remaining = @($rows | Where-Object { Test-Path -LiteralPath (Join-Path $project $_.path) })
    if ($remaining.Count) { throw "$($remaining.Count) retired files still exist" }
    $manifest.status = 'completed_verified'
    $manifest.completed_at = (Get-Date).ToString('o')
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding utf8
}
[pscustomobject]@{Mode=if ($Execute) {'EXECUTED'} else {'DRY_RUN'}; Files=$files.Count; Bytes=$total; Manifest=$manifestPath}
