<# Remove one rejected ASTER pre-gate candidate and its matching generated guide. #>

[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9][a-z0-9_-]{2,80}$')]
    [string]$CandidateId
)

$ErrorActionPreference = 'Stop'
$projectRoot = [System.IO.Path]::GetFullPath((Split-Path -Parent (Split-Path -Parent $PSScriptRoot)))
$candidate = [System.IO.Path]::GetFullPath((Join-Path $projectRoot "art_src\pilot_v2\aster_v2\qwen_edits\$CandidateId"))
$guide = [System.IO.Path]::GetFullPath((Join-Path $projectRoot "art_src\pilot_v2\aster_v2\pose_guides\_aster_static_master_pipeline\$CandidateId"))
foreach ($target in @($candidate, $guide)) {
    $relative = [System.IO.Path]::GetRelativePath($projectRoot, $target)
    if ($relative -eq '..' -or $relative.StartsWith("..$([System.IO.Path]::DirectorySeparatorChar)")) { throw "cleanup target escapes project: $target" }
    if ((Test-Path -LiteralPath $target) -and $PSCmdlet.ShouldProcess($target, 'Remove rejected ASTER pre-gate asset source')) {
        Remove-Item -LiteralPath $target -Recurse -Force
    }
}
