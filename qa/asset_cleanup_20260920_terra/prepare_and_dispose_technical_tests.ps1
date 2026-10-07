[CmdletBinding()]
param(
    [switch]$Execute
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$receiptRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$repoRoot = [IO.Path]::GetFullPath((Join-Path $receiptRoot '..\..'))
$technicalRoot = [IO.Path]::GetFullPath((Join-Path $repoRoot 'motion_lab_v1\qa\technical_tests'))
$manifestPath = Join-Path $receiptRoot 'technical_tests_disposal_manifest.before.tsv'
$soundBeforePath = Join-Path $receiptRoot 'sound_related_preserved.before.tsv'
$mediaBeforePath = Join-Path $receiptRoot 'technical_tests_media_preserved.before.tsv'
$runtimeBeforePath = Join-Path $receiptRoot 'runtime_references.before.json'
$runtimeAfterPath = Join-Path $receiptRoot 'runtime_references.after.json'
$provenanceAuditPath = Join-Path $receiptRoot 'synthetic_provenance.before.json'
$summaryBeforePath = Join-Path $receiptRoot 'inventory.before.json'
$resultPath = Join-Path $receiptRoot 'disposal.result.json'

$videoExtensions = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
@('.avi', '.m4v', '.mkv', '.mov', '.mp4', '.webm') | ForEach-Object { [void]$videoExtensions.Add($_) }
$audioExtensions = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
@('.aac', '.aif', '.aiff', '.flac', '.m4a', '.mid', '.midi', '.mp3', '.ogg', '.opus', '.wav', '.wma') | ForEach-Object { [void]$audioExtensions.Add($_) }

function To-RepositoryRelative([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    if (-not $full.StartsWith($repoRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "PATH_OUTSIDE_REPOSITORY: $full"
    }
    return $full.Substring($repoRoot.Length + 1).Replace('\', '/')
}

function Assert-PathWithin([string]$Path, [string]$Root) {
    $full = [IO.Path]::GetFullPath($Path)
    $base = [IO.Path]::GetFullPath($Root)
    if (-not $full.StartsWith($base + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "PATH_OUTSIDE_APPROVED_ROOT: $full"
    }
}

function Assert-NoReparsePoints([string]$Root) {
    $rootItem = Get-Item -LiteralPath $Root -Force
    if (($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "ROOT_REPARSE_POINT: $Root"
    }
    $links = @(Get-ChildItem -LiteralPath $Root -Force -Recurse -Attributes ReparsePoint -ErrorAction Stop)
    if ($links.Count -ne 0) {
        throw "REPARSE_POINT_PRESENT: $($links[0].FullName)"
    }
}

function Get-Sha256([string]$Path) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
        try {
            $hash = $sha.ComputeHash($stream)
        }
        finally {
            $stream.Dispose()
        }
    }
    finally {
        $sha.Dispose()
    }
    return ([BitConverter]::ToString($hash)).Replace('-', '')
}

function Is-SoundRelated([IO.FileInfo]$File) {
    $relative = To-RepositoryRelative $File.FullName
    return $audioExtensions.Contains($File.Extension) -or $relative -match '(?i)(^|/)(audio|sound|sfx|music|voice)(/|_|$)'
}

function Is-PreservedTechnicalMedia([IO.FileInfo]$File) {
    $relative = To-RepositoryRelative $File.FullName
    return $videoExtensions.Contains($File.Extension) -or $audioExtensions.Contains($File.Extension) -or $relative -match '(?i)(audio|sound|sfx|music|voice)'
}

function Get-TechnicalTopLevelName([IO.FileInfo]$File) {
    Assert-PathWithin $File.FullName $technicalRoot
    $relative = $File.FullName.Substring($technicalRoot.Length + 1)
    return ($relative -split '[\\/]', 2)[0]
}

function Get-TechnicalMediaTopLevelNames([object[]]$Files) {
    $names = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($file in $Files) {
        if (Is-PreservedTechnicalMedia $file) {
            [void]$names.Add((Get-TechnicalTopLevelName $file))
        }
    }
    return ,$names
}

function Get-TechnicalCandidates {
    Assert-NoReparsePoints $technicalRoot
    $files = Get-ChildItem -LiteralPath $technicalRoot -Force -Recurse -File
    $mediaTopLevelNames = Get-TechnicalMediaTopLevelNames $files
    # Preserve an entire fixture directory when it contains audio or video.
    # Its JSON/PNG sidecars can be required to interpret that retained media.
    return @($files | Where-Object { -not $mediaTopLevelNames.Contains((Get-TechnicalTopLevelName $_)) })
}

function Get-TechnicalPreservedMediaFiles([object[]]$Files) {
    $mediaTopLevelNames = Get-TechnicalMediaTopLevelNames $Files
    return @($Files | Where-Object { $mediaTopLevelNames.Contains((Get-TechnicalTopLevelName $_)) })
}

function Write-TsvManifest([string]$Path, [object[]]$Files, [string]$Reason, [string]$AllowedRoot) {
    $writer = [IO.StreamWriter]::new($Path, $false, [Text.UTF8Encoding]::new($false))
    try {
        $writer.WriteLine("relative_path`tabsolute_path`tbytes`tsha256`treason")
        foreach ($file in $Files) {
            Assert-PathWithin $file.FullName $AllowedRoot
            $relative = To-RepositoryRelative $file.FullName
            $hash = Get-Sha256 $file.FullName
            $writer.WriteLine("$relative`t$($file.FullName)`t$($file.Length)`t$hash`t$Reason")
        }
    }
    finally {
        $writer.Dispose()
    }
}

function Read-TsvManifest([string]$Path) {
    $rows = [Collections.Generic.List[object]]::new()
    $first = $true
    foreach ($line in [IO.File]::ReadLines($Path)) {
        if ($first) { $first = $false; continue }
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $parts = $line.Split([char]9, 5)
        if ($parts.Count -ne 5) { throw "MALFORMED_MANIFEST_ROW: $line" }
        $rows.Add([PSCustomObject]@{
            relative_path = $parts[0]
            absolute_path = $parts[1]
            bytes = [int64]$parts[2]
            sha256 = $parts[3]
            reason = $parts[4]
        })
    }
    return $rows.ToArray()
}

function Assert-SyntheticOnlyScope([object[]]$Candidates) {
    $candidatePaths = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($candidate in $Candidates) { [void]$candidatePaths.Add($candidate.FullName) }

    # The scope may contain test metadata, but a file that represents itself as
    # an approved/current production asset is excluded rather than disposed.
    $claims = @(& rg -l -i -g '*.json' -e '"(?:provenance_status|production_provenance|asset_status)"\s*:\s*"(?:real|production|approved|current)"' $technicalRoot 2>$null)
    if ($LASTEXITCODE -gt 1) { throw "PROVENANCE_CLAIM_SCAN_FAILED: $LASTEXITCODE" }
    $candidateClaims = @($claims | ForEach-Object { [IO.Path]::GetFullPath($_) } | Where-Object { $candidatePaths.Contains($_) })
    if ($candidateClaims.Count -ne 0) { throw "CANDIDATE_SELF_DECLARES_PRODUCTION_PROVENANCE: $($candidateClaims -join ', ')" }

    # A synthetic fixture may name its own temporary path. A path reference to
    # another repository area would be real-asset provenance and is out of scope.
    $pathMentions = @(& rg -l -F $repoRoot $technicalRoot 2>$null)
    if ($LASTEXITCODE -gt 1) { throw "EXTERNAL_PATH_SCAN_FAILED: $LASTEXITCODE" }
    $outsideMentions = [Collections.Generic.List[string]]::new()
    foreach ($path in $pathMentions) {
        $full = [IO.Path]::GetFullPath($path)
        if (-not $candidatePaths.Contains($full)) { continue }
        $content = [IO.File]::ReadAllText($full)
        foreach ($match in [regex]::Matches($content, [regex]::Escape($repoRoot) + '[^"\r\n]*')) {
            if (-not $match.Value.StartsWith($technicalRoot, [StringComparison]::OrdinalIgnoreCase)) {
                $outsideMentions.Add($full)
                break
            }
        }
    }
    if ($outsideMentions.Count -ne 0) { throw "CANDIDATE_REFERENCES_REAL_PROJECT_PATH: $($outsideMentions -join ', ')" }
    Write-Json -Path $provenanceAuditPath -Value ([PSCustomObject]@{
        checkedAt = (Get-Date).ToString('o')
        candidateCount = $Candidates.Count
        selfDeclaredProductionProvenanceClaims = 0
        candidateReferencesOutsideTechnicalTests = 0
        status = 'PASS_SYNTHETIC_SCOPE_ONLY'
    })
}

function Get-RuntimeReferences {
    $scan = @('project.godot', 'assets', 'data', 'scenes', 'scripts')
    $matches = @(& rg -l -e 'motion_lab_v1/qa/technical_tests' -e 'motion_lab_v1\\qa\\technical_tests' -e 'qa/technical_tests' -e 'qa\\technical_tests' @scan 2>$null)
    if ($LASTEXITCODE -gt 1) { throw "RUNTIME_REFERENCE_SCAN_FAILED: $LASTEXITCODE" }
    return @($matches | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)
}

function Get-NonRuntimeReferences {
    $matches = @(& rg -l --glob '!motion_lab_v1/qa/technical_tests/**' -e 'motion_lab_v1/qa/technical_tests' -e 'motion_lab_v1\\qa\\technical_tests' -e 'qa/technical_tests' -e 'qa\\technical_tests' . 2>$null)
    if ($LASTEXITCODE -gt 1) { throw "NON_RUNTIME_REFERENCE_SCAN_FAILED: $LASTEXITCODE" }
    return @($matches | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)
}

function Write-Json([string]$Path, [object]$Value) {
    $Value | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Path -Encoding utf8NoBOM
}

if (-not (Test-Path -LiteralPath $technicalRoot -PathType Container)) {
    throw "TECHNICAL_TEST_ROOT_MISSING: $technicalRoot"
}
Assert-PathWithin $technicalRoot $repoRoot

if (-not $Execute) {
    $allTechnicalFiles = @(Get-ChildItem -LiteralPath $technicalRoot -Force -Recurse -File)
    $candidates = Get-TechnicalCandidates
    $technicalMedia = Get-TechnicalPreservedMediaFiles $allTechnicalFiles
    $soundFiles = @(Get-ChildItem -LiteralPath $repoRoot -Force -Recurse -File | Where-Object {
        $_.FullName -notlike "$repoRoot\.git\*" -and $_.FullName -notlike "$receiptRoot\*" -and (Is-SoundRelated $_)
    })

    $runtime = @(Get-RuntimeReferences)
    $nonRuntime = @(Get-NonRuntimeReferences)
    if ($runtime.Count -ne 0) { throw "RUNTIME_REFERENCE_PRESENT_BEFORE_DELETE: $($runtime -join ', ')" }
    Assert-SyntheticOnlyScope $candidates
    Write-TsvManifest -Path $manifestPath -Files $candidates -Reason 'synthetic_technical_test_fixture_not_runtime_or_production_asset' -AllowedRoot $technicalRoot
    Write-TsvManifest -Path $soundBeforePath -Files $soundFiles -Reason 'user_required_sound_preservation' -AllowedRoot $repoRoot
    Write-TsvManifest -Path $mediaBeforePath -Files $technicalMedia -Reason 'video_or_audio_ambiguous_preserved_with_entire_fixture_directory' -AllowedRoot $technicalRoot

    Write-Json -Path $runtimeBeforePath -Value ([PSCustomObject]@{
        checkedAt = (Get-Date).ToString('o')
        scanRoots = @('project.godot', 'assets', 'data', 'scenes', 'scripts')
        technicalTestsRuntimeReferences = $runtime
        technicalTestsRuntimeReferenceCount = $runtime.Count
        nonRuntimeReferences = $nonRuntime
        nonRuntimeReferenceCount = $nonRuntime.Count
        conclusion = 'Only dynamic test/document references are permitted; no runtime reference authorizes preserving disposable synthetic fixtures.'
    })
    Write-Json -Path $summaryBeforePath -Value ([PSCustomObject]@{
        checkedAt = (Get-Date).ToString('o')
        candidateRoot = (To-RepositoryRelative $technicalRoot)
        candidateCount = $candidates.Count
        candidateBytes = [int64](($candidates | Measure-Object -Property Length -Sum).Sum)
        preservedTechnicalMediaCount = $technicalMedia.Count
        preservedTechnicalMediaBytes = [int64](($technicalMedia | Measure-Object -Property Length -Sum).Sum)
        preservedSoundRelatedCount = $soundFiles.Count
        preservedSoundRelatedBytes = [int64](($soundFiles | Measure-Object -Property Length -Sum).Sum)
        candidateManifestSha256 = (Get-Sha256 $manifestPath)
        soundManifestSha256 = (Get-Sha256 $soundBeforePath)
        technicalMediaManifestSha256 = (Get-Sha256 $mediaBeforePath)
        syntheticProvenanceAuditSha256 = (Get-Sha256 $provenanceAuditPath)
        noReparsePoints = $true
        deletionPerformed = $false
    })
    Write-Output "Prepared candidate manifest: $manifestPath"
    exit 0
}

foreach ($required in @($manifestPath, $soundBeforePath, $mediaBeforePath, $runtimeBeforePath, $summaryBeforePath)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "PREPARATION_RECEIPT_REQUIRED: $required" }
}
Assert-NoReparsePoints $technicalRoot
$runtimeNow = @(Get-RuntimeReferences)
if ($runtimeNow.Count -ne 0) { throw 'RUNTIME_REFERENCE_PRESENT_BEFORE_EXECUTION' }
$before = Get-Content -LiteralPath $summaryBeforePath -Raw | ConvertFrom-Json
if ((Get-Sha256 $manifestPath) -ne $before.candidateManifestSha256) { throw 'MANIFEST_CHANGED' }
$rows = Read-TsvManifest $manifestPath
if ($rows.Count -eq 0) { throw 'EMPTY_DISPOSAL_MANIFEST' }

# Verify every recorded byte before any deletion. This prevents a partially changed
# technical-test tree from being treated as the reviewed scope.
foreach ($row in $rows) {
    Assert-PathWithin $row.absolute_path $technicalRoot
    if (-not (Test-Path -LiteralPath $row.absolute_path -PathType Leaf)) { throw "CANDIDATE_MISSING_BEFORE_DELETE: $($row.absolute_path)" }
    $file = Get-Item -LiteralPath $row.absolute_path -Force
    if (($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "CANDIDATE_REPARSE_POINT: $($row.absolute_path)" }
    if ($file.Length -ne $row.bytes) { throw "CANDIDATE_SIZE_CHANGED: $($row.absolute_path)" }
    if ((Get-Sha256 $row.absolute_path) -ne $row.sha256) { throw "CANDIDATE_HASH_CHANGED: $($row.absolute_path)" }
}

foreach ($row in $rows) {
    # Deliberately one literal file at a time: no glob and no recursive deletion.
    Remove-Item -LiteralPath $row.absolute_path -Force -ErrorAction Stop
}

$remainingCandidates = Get-TechnicalCandidates
if ($remainingCandidates.Count -ne 0) { throw "UNEXPECTED_REMAINING_CANDIDATES: $($remainingCandidates.Count)" }

$soundRows = Read-TsvManifest $soundBeforePath
$soundFailures = [Collections.Generic.List[string]]::new()
foreach ($row in $soundRows) {
    if (-not (Test-Path -LiteralPath $row.absolute_path -PathType Leaf)) { $soundFailures.Add("MISSING $($row.relative_path)"); continue }
    $current = Get-Item -LiteralPath $row.absolute_path -Force
    if ($current.Length -ne $row.bytes -or (Get-Sha256 $row.absolute_path) -ne $row.sha256) { $soundFailures.Add("CHANGED $($row.relative_path)") }
}
if ($soundFailures.Count -ne 0) { throw "SOUND_PRESERVATION_FAILED: $($soundFailures -join '; ')" }

$mediaRows = Read-TsvManifest $mediaBeforePath
$mediaFailures = [Collections.Generic.List[string]]::new()
foreach ($row in $mediaRows) {
    if (-not (Test-Path -LiteralPath $row.absolute_path -PathType Leaf)) { $mediaFailures.Add("MISSING $($row.relative_path)"); continue }
    $current = Get-Item -LiteralPath $row.absolute_path -Force
    if ($current.Length -ne $row.bytes -or (Get-Sha256 $row.absolute_path) -ne $row.sha256) { $mediaFailures.Add("CHANGED $($row.relative_path)") }
}
if ($mediaFailures.Count -ne 0) { throw "TECHNICAL_MEDIA_PRESERVATION_FAILED: $($mediaFailures -join '; ')" }

$runtimeAfter = @(Get-RuntimeReferences)
Write-Json -Path $runtimeAfterPath -Value ([PSCustomObject]@{
    checkedAt = (Get-Date).ToString('o')
    scanRoots = @('project.godot', 'assets', 'data', 'scenes', 'scripts')
    technicalTestsRuntimeReferences = $runtimeAfter
    technicalTestsRuntimeReferenceCount = $runtimeAfter.Count
})
if ($runtimeAfter.Count -ne 0) { throw "RUNTIME_REFERENCE_PRESENT_AFTER_DELETE: $($runtimeAfter -join ', ')" }

$deletedBytes = [int64](($rows | Measure-Object -Property bytes -Sum).Sum)
Write-Json -Path $resultPath -Value ([PSCustomObject]@{
    completedAt = (Get-Date).ToString('o')
    deletionScope = (To-RepositoryRelative $technicalRoot)
    deletedFileCount = $rows.Count
    deletedBytes = $deletedBytes
    manifestSha256 = (Get-Sha256 $manifestPath)
    remainingDisposableCandidateCount = $remainingCandidates.Count
    soundPreservation = [PSCustomObject]@{ fileCount = $soundRows.Count; status = 'PASS_EXACT_BYTES_AND_SHA256' }
    technicalMediaPreservation = [PSCustomObject]@{ fileCount = $mediaRows.Count; status = 'PASS_EXACT_BYTES_AND_SHA256' }
    runtimeReferencesBefore = ((Get-Content -LiteralPath $runtimeBeforePath -Raw | ConvertFrom-Json).technicalTestsRuntimeReferenceCount)
    runtimeReferencesAfter = $runtimeAfter.Count
    deletionMethod = 'One file per Remove-Item -LiteralPath; no glob; no recursive delete.'
})
Write-Output "Disposed $($rows.Count) synthetic technical-test fixture files ($deletedBytes bytes)."
