$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$libraryRoot = [IO.Path]::GetFullPath('D:/AI 종합 폴더/Games/voice, image asset/voice & sound/sound')
$manifestPath = Join-Path $projectRoot 'sound/music/allocation.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$test = Get-Content -LiteralPath (Join-Path $projectRoot 'qa/music_integration_20260920/runtime_check.json') -Raw | ConvertFrom-Json
if (-not $test.pass -or $test.checks -lt 48) { throw 'Runtime gate has not passed' }
$scope = @()
foreach ($track in $manifest.tracks) {
    $sourcePath = [IO.Path]::GetFullPath($track.source)
    $originalPath = [IO.Path]::GetFullPath((Join-Path $projectRoot $track.original))
    $runtimePath = [IO.Path]::GetFullPath((Join-Path $projectRoot $track.runtime))
    if (-not $sourcePath.StartsWith($libraryRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Source escaped exact library root' }
    foreach ($target in @($originalPath, $runtimePath)) {
        if (-not $target.StartsWith($projectRoot + '\sound\music\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Destination escaped project music root' }
    }
    if ((Get-FileHash -LiteralPath $originalPath -Algorithm SHA256).Hash.ToLower() -ne $track.original_sha256) { throw 'Original copy hash mismatch' }
    if ((Get-FileHash -LiteralPath $runtimePath -Algorithm SHA256).Hash.ToLower() -ne $track.runtime_sha256) { throw 'Runtime hash mismatch' }
    if (Test-Path -LiteralPath $sourcePath) {
        if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) { throw 'Deletion target is not a file' }
        if ((Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLower() -ne $track.original_sha256) { throw 'Shared source changed; abort all deletion' }
    } elseif (-not $track.source_removed) { throw 'Unexpected missing shared source' }
    $scope += [pscustomobject]@{source=$sourcePath; preserved_original=$originalPath; sha256=$track.original_sha256}
}
# Pre-deletion receipt for the exact user-authorized files; never recurse.
$receipt = Join-Path $projectRoot 'qa/music_integration_20260920/source_retirement.json'
@{project='SABLE CIRCUIT'; recoverable_from='sound/music/originals'; files=$scope; status='HASH_VERIFIED_BEFORE_REMOVAL'} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receipt -Encoding utf8
foreach ($track in $manifest.tracks) {
    if (Test-Path -LiteralPath $track.source) { Remove-Item -LiteralPath $track.source }
    if (Test-Path -LiteralPath $track.source) { throw 'Source removal failed' }
    $track.source_removed = $true
}
$manifest | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $manifestPath -Encoding utf8
@{project='SABLE CIRCUIT'; recoverable_from='sound/music/originals'; files=$scope; status='REMOVED_FROM_SHARED_POOL_ORIGINALS_RETAINED_IN_PROJECT'} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receipt -Encoding utf8
Write-Output ('RETIRED_SHARED_FILES=' + $scope.Count)
