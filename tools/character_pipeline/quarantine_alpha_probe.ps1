$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath('D:\AI 종합 폴더\Games\Sable-circuit')
$sourcePath = [IO.Path]::GetFullPath((Join-Path $projectRoot 'art_src\characters\mica\rigged_v2\source_alpha_probe_r1'))
$targetPath = [IO.Path]::GetFullPath((Join-Path $projectRoot 'artifacts\quarantine\generation_diagnostics\mica_native_alpha_probe_r1'))
$quarantineRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot 'artifacts\quarantine\generation_diagnostics'))
if (-not $sourcePath.StartsWith($projectRoot + '\') -or -not $targetPath.StartsWith($quarantineRoot + '\')) { throw 'Outside exact project scope' }
if (-not (Test-Path -LiteralPath $sourcePath -PathType Container) -or (Test-Path -LiteralPath $targetPath)) { throw 'Missing source or occupied target' }
$audit = Get-Content -LiteralPath (Join-Path $sourcePath 'NATIVE_ALPHA_AUDIT_R1.json') -Raw | ConvertFrom-Json
if ($audit.verdict -ne 'FAIL' -or $audit.mode -ne 'RGB') { throw 'Not the reviewed failed probe' }
$entries = @(Get-ChildItem -LiteralPath $sourcePath -File -Recurse | ForEach-Object {
    $relative = [IO.Path]::GetRelativePath($sourcePath, $_.FullName)
    [ordered]@{ old_path=$_.FullName; quarantined_path=(Join-Path $targetPath $relative); sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower() }
})
# Derived inventory, not a source/code rewrite. All historic refs remain stored
# verbatim; the explicit mapping records their quarantine relocation.
$inventoryPath = Join-Path $quarantineRoot 'mica_native_alpha_probe_r1_RELOCATION.json'
if (Test-Path -LiteralPath $inventoryPath) { throw 'Preserve previous inventory' }
[ordered]@{status='FAIL_NOT_PROMOTABLE'; reason='RGB painted checkerboard, no alpha'; deleted=$false; files=$entries} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $inventoryPath -Encoding utf8
Move-Item -LiteralPath $sourcePath -Destination $targetPath
foreach ($entry in $entries) {
    if ((Get-FileHash -LiteralPath $entry.quarantined_path -Algorithm SHA256).Hash.ToLower() -ne $entry.sha256) { throw 'Quarantine hash verification failed' }
}
Write-Output "Quarantined $($entries.Count) files; nothing deleted. $targetPath"
