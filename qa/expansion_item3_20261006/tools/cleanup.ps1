$ErrorActionPreference='Stop'
$regressionProcesses=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python' -and $_.CommandLine -match 'run_regression_suite\.py' })
if($regressionProcesses.Count){throw 'Existing regression runner; QA and cleanup held'}
$projectRoot=(Resolve-Path -LiteralPath '.').Path
$expectedProject='D:\AI 종합 폴더\Games\Sable-circuit'
if($projectRoot -ne $expectedProject){throw 'Unexpected working root'}
$taskRoot=(Resolve-Path -LiteralPath '.cache/diag/expansion_item3_20261006').Path
$qaRoot=(Resolve-Path -LiteralPath 'qa/expansion_item3_20261006').Path
$expectedTask=[IO.Path]::GetFullPath((Join-Path $projectRoot '.cache/diag/expansion_item3_20261006'))
if($taskRoot -ne $expectedTask -or -not $taskRoot.StartsWith($projectRoot+'\.cache\',[StringComparison]::OrdinalIgnoreCase)){throw 'Cleanup target outside own cache'}
$entries=@(Get-ChildItem -LiteralPath $taskRoot -Recurse -Force)
if(@($entries | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count){throw 'Reparse point in cleanup scope'}
foreach($name in @('baseline_contract_save.log','base_ui_fixed_stdout.log','lab_size_stdout.log')){
    Copy-Item -LiteralPath (Join-Path $taskRoot $name) -Destination (Join-Path $qaRoot ('records/'+$name))
}
Copy-Item -LiteralPath (Join-Path $taskRoot 'cleanup.ps1') -Destination (Join-Path $qaRoot 'tools/cleanup.ps1')
Copy-Item -LiteralPath (Join-Path $taskRoot 'native/capture_report.json') -Destination (Join-Path $qaRoot 'records/native_capture_report.json')
$capturePath=Join-Path $qaRoot 'captures/capture_report.json'
$captureReport=Get-Content -LiteralPath $capturePath -Raw -Encoding UTF8 | ConvertFrom-Json
foreach($row in $captureReport.captures){
    $row | Add-Member -NotePropertyName source_capture -NotePropertyValue $row.capture
    $row.capture='res://qa/expansion_item3_20261006/captures/'+$row.id+'.png'
}
$captureReport | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $capturePath -Encoding UTF8
$qaFiles=@(Get-ChildItem -LiteralPath $qaRoot -Recurse -File)
$qaHashes=@{}
foreach($file in $qaFiles){
    $hash=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    if(-not $qaHashes.ContainsKey($hash)){$qaHashes[$hash]=$file.FullName.Substring($projectRoot.Length+1).Replace('\','/')}
}
$rows=@()
$fileCount=0
$totalBytes=0L
foreach($file in ($entries | Where-Object { -not $_.PSIsContainer })){
    $absolute=[IO.Path]::GetFullPath($file.FullName)
    if(-not $absolute.StartsWith($taskRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'File outside own task cache'}
    $hash=(Get-FileHash -LiteralPath $absolute -Algorithm SHA256).Hash.ToLowerInvariant()
    $replacement=if($qaHashes.ContainsKey($hash)){$qaHashes[$hash]}else{$null}
    $relative=$absolute.Substring($projectRoot.Length+1).Replace('\','/')
    if($relative.EndsWith('.png') -and $null -eq $replacement){throw 'PNG without a byte-identical final QA replacement'}
    $rows+=@{path=$relative;sha256=$hash;bytes=$file.Length;replacement=$replacement;reason=if($replacement){'Byte-identical final QA evidence retained'}else{'Superseded item-3 editing or intermediate test scratch; final test evidence retained'}}
    $fileCount+=1
    $totalBytes+=$file.Length
}
$manifest=@{schema=1;authorization='User: remove unneeded materials and test copies after work';scope=$taskRoot;gates=@{quick='20261006_003832_quick 56/56 PASS';full_only='20261006_004731_custom 3/3 PASS';native_png='7/7 validated; final QA hashes matched';active_runner=0};planned_files=$fileCount;bytes=$totalBytes;rows=$rows;deleted_files=0;status='RECORDED_BEFORE_DISPOSAL'}
$manifestPath=Join-Path $qaRoot 'records/cleanup_manifest.json'
$manifest | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
# The exact resolved D: cache root and all descendants were verified above.
Remove-Item -LiteralPath $taskRoot -Recurse -Force
if(Test-Path -LiteralPath $taskRoot){throw 'Cleanup left its task directory'}
$manifest.deleted_files=$fileCount
$manifest.status='COMPLETE'
$manifest.disposed_at_utc=(Get-Date).ToUniversalTime().ToString('o')
$manifest | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
$reportPath=Join-Path $qaRoot 'README_KO.md'
$report=Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8
$report=$report.Replace('현재 작업의 중복 캡처·대조 실행 사본과 일회성 편집 초안을 `.cache`에서 정리한다.','현재 작업의 중복 캡처·대조 실행 사본과 일회성 편집 초안 '+$fileCount+'개('+([math]::Round($totalBytes/1MB,2))+' MiB)를 지정된 `.cache` 폴더에서 삭제했다.')
$report=$report.Replace('실제 삭제 범위와 해시는 `records/cleanup_manifest.json`에 기록하며','실제 삭제 범위와 해시는 [정리 기록](records/cleanup_manifest.json)에 기록했으며')
$report | Set-Content -LiteralPath $reportPath -Encoding UTF8
Write-Output ('CLEANUP: removed '+$fileCount+' files, '+$totalBytes+' bytes; final QA evidence retained')
