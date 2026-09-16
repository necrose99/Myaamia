# Configuration
$chunkSize = 10
$remote = "origin"
$branch = "master"

# Get a list of all local commit hashes that are not on the remote server
$commits = git log ${remote}/${branch}..${branch} --format="%H" | Select-Object -Last 999999

if ($null -eq $commits -or $commits.Count -eq 0) {
    Write-Host "No pending commits found to push." -ForegroundColor Green
    exit
}

$totalCommits = $commits.Count
Write-Host "Found $totalCommits pending commits. Pushing in batches of $chunkSize..." -ForegroundColor Cyan

# Loop through the commits using the specified chunk size
for ($i = 0; $i -lt $totalCommits; $i += $chunkSize) {
    # Pick the target commit at the end of the current batch
    $targetIndex = [Math]::Min($i + $chunkSize - 1, $totalCommits - 1)
    $targetCommit = $commits[$targetIndex]
    
    $batchNum = [int]($i / $chunkSize) + 1
    # FIXED: Wrapped batchNum in ${} to prevent PowerShell from misinterpreting the colon
    Write-Host "🚀 Batch ${batchNum}: Pushing up to commit $targetCommit..." -ForegroundColor Yellow
    
    # Execute the push command
    git push $remote "${targetCommit}:${branch}"
    
    # If the push fails, stop execution immediately to avoid stacking errors
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Push failed at batch ${batchNum}. Stopping script."
        exit
    }
}

Write-Host "Success! All batches pushed completely." -ForegroundColor Green
