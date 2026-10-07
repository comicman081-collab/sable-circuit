param([Parameter(Mandatory)][ValidateSet('Quarantine', 'Purge', 'Restore')][string]$Phase,
      [ValidatePattern('^asset_cleanup_[a-z0-9_]+$')][string]$Batch = 'asset_cleanup_20260911')
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$report = Join-Path $root "qa/$Batch"
$quarantineName = if ($Batch -eq 'asset_cleanup_20260911') { '20260911_unused_data' } else { $Batch }
$quarantineRoot = Join-Path $root "quarantine_cleanup/$quarantineName"
$payload = Join-Path $quarantineRoot 'payload'
$separator = [IO.Path]::DirectorySeparatorChar

function Assert-Within([string]$Path, [string]$Base) {
    $full = [IO.Path]::GetFullPath($Path)
    $baseFull = [IO.Path]::GetFullPath($Base).TrimEnd($separator) + $separator
    if (-not $full.StartsWith($baseFull, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Target escapes its explicit boundary: $full"
    }
    return $full
}

function Assert-NoReparse([string]$Path) {
    $current = $Path
    while ($current -and $current -ne $root) {
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Reparse point in operation target: $current"
            }
        }
        $current = [IO.Path]::GetDirectoryName($current)
    }
}

$payload = Assert-Within $payload $quarantineRoot
Assert-NoReparse $payload
$seal = Get-Content -LiteralPath (Join-Path $report 'seal.json') -Raw | ConvertFrom-Json
foreach ($pair in @(@('retirement_manifest.json', 'manifestSHA256'),
                    @('move_groups.json', 'groupsSHA256'), @('protected_before.json', 'protectedSHA256'))) {
    $actual = (Get-FileHash -LiteralPath (Join-Path $report $pair[0]) -Algorithm SHA256).Hash
    if ($actual -ne $seal.($pair[1])) { throw "Changed sealed input: $($pair[0])" }
}

if ($Phase -eq 'Restore') {
    $journalPath = Join-Path $report 'quarantine_moves.jsonl'
    $moves = @(Get-Content -LiteralPath $journalPath | ConvertFrom-Json)
    foreach ($group in $moves) {
        $source = Assert-Within (Join-Path $payload $group.path) $payload
        $destination = Assert-Within (Join-Path $root $group.path) $root
        Assert-NoReparse $source
        Assert-NoReparse $destination
        if (-not (Test-Path -LiteralPath $source) -or (Test-Path -LiteralPath $destination)) {
            throw "Cannot restore without overwriting/missing payload: $($group.path)"
        }
    }
    foreach ($group in $moves) {
        $source = Assert-Within (Join-Path $payload $group.path) $payload
        $destination = Assert-Within (Join-Path $root $group.path) $root
        $parent = [IO.Path]::GetDirectoryName($destination)
        if (-not (Test-Path -LiteralPath $parent)) { $null = New-Item -ItemType Directory -Path $parent -Force }
        Move-Item -LiteralPath $source -Destination $destination
    }
    Write-Output "RESTORED: $($moves.Count) moved groups. Original journal retained."
} elseif ($Phase -eq 'Quarantine') {
    $groups = @(Get-Content -LiteralPath (Join-Path $report 'move_groups.json') -Raw | ConvertFrom-Json)
    # Check every resolved target before the first move. No broad root, code,
    # installed tool/model or sibling worktree can be admitted.
    foreach ($group in $groups) {
        $relative = $group.path.Replace('\', '/')
        if ($relative -notmatch '^(artifacts(/|$)|art_src/(characters/(mica(/|$)|_technical_generation_requests(/|$))|pilot_v2(/|$))|motion_lab_v1/(experiments(/|$)|art/aster/previous(/|$)|qa(/|$))|assets/units/operators/mica/fast_runtime_v1(/|$))' -and
            $relative -notmatch '^[^:]+/__pycache__(/|$)') {
            throw "Group outside reviewed generated-output scopes: $relative"
        }
        $source = Assert-Within (Join-Path $root $relative) $root
        $destination = Assert-Within (Join-Path $payload $relative) $payload
        Assert-NoReparse $source
        Assert-NoReparse $destination
        if (-not (Test-Path -LiteralPath $source)) { throw "Missing original: $source" }
        if (Test-Path -LiteralPath $destination) { throw "Quarantine already occupied: $destination" }
    }
    $null = New-Item -ItemType Directory -Path $payload -Force
    $count = 0
    $journalPath = Join-Path $report 'quarantine_moves.jsonl'
    if (Test-Path -LiteralPath $journalPath) { throw 'Move journal already exists; inspect partial operation before resuming' }
    $journal = [IO.StreamWriter]::new($journalPath, $false, [Text.UTF8Encoding]::new($false))
    try {
        foreach ($group in $groups) {
            $source = Assert-Within (Join-Path $root $group.path) $root
            $destination = Assert-Within (Join-Path $payload $group.path) $payload
            $parent = [IO.Path]::GetDirectoryName($destination)
            if (-not (Test-Path -LiteralPath $parent)) { $null = New-Item -ItemType Directory -Path $parent -Force }
            Move-Item -LiteralPath $source -Destination $destination
            $journal.WriteLine(($group | ConvertTo-Json -Compress))
            $journal.Flush()
            $count++
            if ($count % 100 -eq 0) { Write-Output "Quarantined groups: $count/$($groups.Count)" }
        }
    } finally { $journal.Dispose() }
    Write-Output "QUARANTINE COMPLETE: $count groups, $($seal.fileCount) files. Nothing purged yet."
} else {
    $verification = Get-Content -LiteralPath (Join-Path $report 'quarantined_verification.json') -Raw | ConvertFrom-Json
    $runtime = Get-Content -LiteralPath (Join-Path $report 'runtime_validation.json') -Raw | ConvertFrom-Json
    if ($verification.status -ne 'PASS' -or $verification.manifestSHA256 -ne $seal.manifestSHA256 -or $runtime.status -ne 'PASS') {
        throw 'Exact quarantine verification and current runtime validation must PASS before purge'
    }
    # Recheck the payload immediately before permanent deletion: exact manifest,
    # no added files and no changed contents. Never delete the workspace itself.
    $manifest = @(Get-Content -LiteralPath (Join-Path $report 'retirement_manifest.json') -Raw | ConvertFrom-Json)
    $expected = [Collections.Generic.Dictionary[string,object]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($row in $manifest) { $expected.Add($row.path.Replace('/', '\'), $row) }
    $items = @(Get-ChildItem -LiteralPath $payload -Force -Recurse)
    if (@($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) {
        throw 'Reparse point appeared in quarantine'
    }
    $files = @($items | Where-Object { -not $_.PSIsContainer })
    if ($files.Count -ne $manifest.Count) { throw 'Quarantine file count changed' }
    $count = 0
    foreach ($file in $files) {
        $relative = $file.FullName.Substring($payload.Length + 1)
        if (-not $expected.ContainsKey($relative)) { throw "Unexpected quarantine file: $relative" }
        $row = $expected[$relative]
        if ($file.Length -ne $row.bytes -or (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash -ne $row.sha256) {
            throw "Quarantine content changed: $relative"
        }
        $count++
        if ($count % 5000 -eq 0) { Write-Output "Purge preflight: $count/$($files.Count)" }
    }
    $validatedTarget = Assert-Within $payload $quarantineRoot
    Assert-NoReparse $validatedTarget
    Remove-Item -LiteralPath $validatedTarget -Recurse -Force
    if (Test-Path -LiteralPath $validatedTarget) { throw 'Payload still exists after purge' }
    Write-Output "PURGED: $($seal.fileCount) files, $($seal.bytes) bytes. Hash manifest retained in $report."
}
