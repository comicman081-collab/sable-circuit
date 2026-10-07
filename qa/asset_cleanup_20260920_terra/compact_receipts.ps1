$ErrorActionPreference = 'Stop'
# Keep exact retirement evidence without leaving a redundant 100+ MB TSV.
$receipt = Join-Path $PSScriptRoot 'technical_tests_disposal_manifest.before.tsv'
$result = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'disposal.result.json') -Raw | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $receipt -Algorithm SHA256).Hash -ne $result.manifestSha256) { throw 'Receipt hash mismatch' }
$archive = $receipt + '.gz'
if (Test-Path -LiteralPath $archive) { throw 'Archive already exists' }
$inputStream = [IO.File]::OpenRead($receipt)
$outputStream = [IO.File]::Create($archive)
$gzip = [IO.Compression.GZipStream]::new($outputStream, [IO.Compression.CompressionLevel]::Optimal)
try { $inputStream.CopyTo($gzip) } finally { $inputStream.Dispose(); $gzip.Dispose(); $outputStream.Dispose() }
$compressed = [IO.File]::OpenRead($archive)
$unzip = [IO.Compression.GZipStream]::new($compressed, [IO.Compression.CompressionMode]::Decompress)
$sha = [Security.Cryptography.SHA256]::Create()
try { $restoredHash = [Convert]::ToHexString($sha.ComputeHash($unzip)) } finally { $sha.Dispose(); $unzip.Dispose(); $compressed.Dispose() }
if ($restoredHash -ne $result.manifestSha256) { throw 'Archive round-trip hash mismatch' }
# Only this newly generated, byte-verified redundant receipt is removed.
Remove-Item -LiteralPath $receipt
[pscustomobject]@{ archive = $archive; sha256 = (Get-FileHash -LiteralPath $archive).Hash; original_sha256 = $restoredHash; verified = $true } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'compressed_receipt.json') -Encoding utf8NoBOM
