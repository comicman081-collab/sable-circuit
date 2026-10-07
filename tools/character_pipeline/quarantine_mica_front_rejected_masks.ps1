$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath('D:\AI 종합 폴더\Games\Sable-circuit')
$sourceRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot 'art_src\characters\mica\rigged_v2\source_front_r1'))
$targetRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot 'artifacts\quarantine\generation_diagnostics\mica_front_source_masks_r1_r2'))
if (-not $sourceRoot.StartsWith($projectRoot + '\') -or -not $targetRoot.StartsWith((Join-Path $projectRoot 'artifacts\quarantine') + '\')) { throw 'Outside exact scope' }
if (Test-Path -LiteralPath $targetRoot) { throw 'Preserve existing quarantine' }
$current = Get-Content -LiteralPath (Join-Path $sourceRoot 'SOURCE_RECEIPT_R3.json') -Raw | ConvertFrom-Json
if ($current.subject_sha256 -ne '2a86ba90e852390dbc8c4179aeb5dcda938e045d66a74f8d05d61202430f9a31') { throw 'Current R3 not verified' }
$files = @('boots_MASK_R1.png','boots_MASK_R2.png','coat_MASK_R1.png','coat_MASK_R2.png','face_MASK_R1.png','face_MASK_R2.png','trousers_MASK_R1.png','trousers_MASK_R2.png','IMAGEGEN_PROVENANCE_R1.json','IMAGEGEN_PROVENANCE_R2.json','S_LANDMARKS_R1.json','S_LANDMARKS_R2.json','SOURCE_AUDIT_R1.json','SOURCE_AUDIT_R2.json','SOURCE_MANIFEST_R1.json','SOURCE_MANIFEST_R2.json','SOURCE_REVIEW_NATIVE_2304x1920.png','SOURCE_REVIEW_R2_NATIVE_2304x1920.png','PONYTAIL_SOURCE_REVIEW_R2.md','REVIEW_1080P_R2.json')
$entries = @($files | ForEach-Object {
    $source = [IO.Path]::GetFullPath((Join-Path $sourceRoot $_))
    $target = [IO.Path]::GetFullPath((Join-Path $targetRoot $_))
    if (-not $source.StartsWith($sourceRoot+'\') -or -not $target.StartsWith($targetRoot+'\')) { throw 'Invalid exact file target' }
    $relative = [IO.Path]::GetRelativePath($projectRoot,$source).Replace('\','/')
    if ($current.bindings.PSObject.Properties.Name -contains $relative) { throw 'Current source still references retired file' }
    [ordered]@{old_path=$source; quarantined_path=$target; sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLower()}
})
New-Item -ItemType Directory -Path $targetRoot | Out-Null
[ordered]@{status='FAIL_NOT_PROMOTABLE'; reason='R1 chroma-containing masks; R2 thigh strap contamination'; deleted=$false; files=$entries; shared_source_preserved_in_active_folder=$true} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $targetRoot 'RELOCATION.json') -Encoding utf8
foreach ($entry in $entries) {
    Move-Item -LiteralPath $entry.old_path -Destination $entry.quarantined_path
    if ((Get-FileHash -LiteralPath $entry.quarantined_path -Algorithm SHA256).Hash.ToLower() -ne $entry.sha256) { throw 'Quarantine hash mismatch' }
}
# Copies preserve source context; current selected source is neither removed nor
# retired. Historic manifest references are resolved through RELOCATION.json.
foreach ($name in @('MICA_C03_S_NEUTRAL_RIG_GREEN_R1.png','prompt.txt','request.json')) {
    Copy-Item -LiteralPath (Join-Path $sourceRoot $name) -Destination (Join-Path $targetRoot $name)
}
Write-Output "Quarantined $($entries.Count) failed annotation/evidence files; source and approved R3 remain active. Nothing deleted."
