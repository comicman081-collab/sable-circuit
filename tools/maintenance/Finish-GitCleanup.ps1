param([Parameter(Mandatory)][ValidateSet('QuarantineLoose', 'Purge')][string]$Phase)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$report = Join-Path $root 'qa/asset_cleanup_20260911_additional'
$quarantine = Join-Path $root 'quarantine_cleanup/asset_cleanup_20260911_additional'
$objectRoot = Join-Path $root '.git/objects'
$writers = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('git.exe', 'git-lfs.exe', 'git-remote-https.exe') })
if ($writers.Count) { throw 'Git process is active; do not remove objects concurrently' }

function Bounded([string]$Path, [string]$Base) {
    $value = [IO.Path]::GetFullPath($Path)
    if (-not $value.StartsWith([IO.Path]::GetFullPath($Base).TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "Target outside explicit boundary: $value"
    }
    $current = $value
    while ($current -and $current -ne $root) {
        if (Test-Path -LiteralPath $current) {
            if ((Get-Item -LiteralPath $current -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Reparse target: $current"
            }
        }
        $current = [IO.Path]::GetDirectoryName($current)
    }
    return $value
}

if ($Phase -eq 'QuarantineLoose') {
    $manifestPath = Join-Path $report 'git_loose_retirement.json'
    if (Test-Path -LiteralPath $manifestPath) { throw 'Loose-object retirement already recorded' }
    $protected = [Collections.Generic.HashSet[string]]::new([string[]](Get-Content -LiteralPath (Join-Path $report 'git_protected_objects.json') -Raw | ConvertFrom-Json))
    $unreachable = [Collections.Generic.HashSet[string]]::new()
    foreach ($row in (Get-Content -LiteralPath (Join-Path $report 'git_unreachable_objects.json') -Raw | ConvertFrom-Json)) { $null = $unreachable.Add($row.oid) }
    $cutoff = [DateTimeOffset]::Parse((Get-Content -LiteralPath (Join-Path $report 'git_before.json') -Raw | ConvertFrom-Json).capturedAt).UtcDateTime
    $rows = [Collections.Generic.List[object]]::new()
    foreach ($directory in Get-ChildItem -LiteralPath $objectRoot -Directory -Force) {
        if ($directory.Name -notmatch '^[0-9a-f]{2}$') { continue }
        foreach ($file in Get-ChildItem -LiteralPath $directory.FullName -File -Force) {
            $oid = $directory.Name + $file.Name
            $object = $file.Name -match '^[0-9a-f]{38}$' -and $unreachable.Contains($oid) -and -not $protected.Contains($oid)
            $temporary = $file.Name -like 'tmp_obj_*' -and $file.LastWriteTimeUtc -lt $cutoff
            if (-not ($object -or $temporary)) { continue }
            $source = Bounded $file.FullName $objectRoot
            $relative = $source.Substring($root.Length + 1).Replace('\', '/')
            $destination = Bounded (Join-Path $quarantine ('git_loose/' + $relative)) $quarantine
            $rows.Add([pscustomobject]@{path=$relative;quarantinePath=$destination.Substring($root.Length + 1).Replace('\', '/');bytes=$file.Length;sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant();reason=$(if ($object) {'unreachable_loose_object'} else {'stale_interrupted_git_temporary_object'})})
        }
    }
    # Generated forensic manifest precedes every move.
    $rows.ToArray() | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding utf8
    foreach ($row in $rows) {
        $source = Bounded (Join-Path $root $row.path) $objectRoot
        $destination = Bounded (Join-Path $root $row.quarantinePath) $quarantine
        if (Test-Path -LiteralPath $destination) { throw "Occupied quarantine: $destination" }
        $null = New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($destination)) -Force
        Move-Item -LiteralPath $source -Destination $destination
    }
    Write-Output "Quarantined $($rows.Count) unreachable loose objects/stale temporary files."
} else {
    $verified = Get-Content -LiteralPath (Join-Path $report 'git_quarantine_verification.json') -Raw | ConvertFrom-Json
    $runtime = Get-Content -LiteralPath (Join-Path $root 'qa/asset_cleanup_20260911_additional_files/runtime_validation.json') -Raw | ConvertFrom-Json
    if ($verified.status -ne 'PASS' -or $runtime.status -ne 'PASS' -or $verified.quarantinedObjects -le 0) {
        throw 'Git protection and app tests must PASS with an actual unreachable backup'
    }
    $rows = [Collections.Generic.List[object]]::new()
    foreach ($row in (Get-Content -LiteralPath (Join-Path $report 'git_quarantine_manifest.json') -Raw | ConvertFrom-Json)) { $rows.Add($row) }
    foreach ($row in (Get-Content -LiteralPath (Join-Path $report 'git_loose_retirement.json') -Raw | ConvertFrom-Json)) {
        $rows.Add([pscustomobject]@{path=$row.quarantinePath;bytes=$row.bytes;sha256=$row.sha256})
    }
    foreach ($row in $rows) {
        $target = Bounded (Join-Path $root $row.path) $quarantine
        $item = Get-Item -LiteralPath $target -Force
        if ($item.PSIsContainer -or $item.Length -ne $row.bytes -or (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $row.sha256) {
            throw "Changed quarantine file: $target"
        }
    }
    foreach ($row in $rows) {
        $target = Bounded (Join-Path $root $row.path) $quarantine
        Remove-Item -LiteralPath $target -Force
    }
    $result = [pscustomobject]@{status='PURGED';files=$rows.Count;quarantinedBytesRemoved=($rows | Measure-Object bytes -Sum).Sum;historyRewritten=$false;checkedAt=(Get-Date -Format o)}
    $result | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $report 'git_purged.json') -Encoding utf8
    $result | ConvertTo-Json
}
