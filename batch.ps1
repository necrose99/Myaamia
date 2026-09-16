cd "C:\Users\black\GitHub\Myaamia"

$branch = (git rev-parse --abbrev-ref HEAD).Trim()
$remote = "origin"
$unpushedHashes = @(git log "${remote}/${branch}..${branch}" --reverse --format=format:%H)

if ($unpushedHashes.Count -eq 0 -or $unpushedHashes -eq "") {
    Write-Host "No unpushed commits found!" -ForegroundColor Green
    Read-Host "Press Enter to exit"
} else {
    Write-Host "Found $($unpushedHashes.Count) commits. Starting chunked push..." -ForegroundColor Cyan
    $batchSize = 5
    $counter = 0

    foreach ($hash in $unpushedHashes) {
        $counter++
        if ($counter % $batchSize -eq 0) {
            Write-Host "Trying batch up to: $hash" -ForegroundColor Yellow
            git push $remote "${hash}:refs/heads/${branch}"
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host "`n[ERROR] Git push failed at commit $hash." -ForegroundColor Red
                Write-Host "The window is being held open so you can read the error above." -ForegroundColor Cyan
                Read-Host "Press Enter to close this window"
                break
            }
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Trying final push..." -ForegroundColor Yellow
        git push $remote "HEAD:refs/heads/${branch}"
        if ($LASTEXITCODE -ne 0) {
            Read-Host "Final push failed. Press Enter to exit"
        } else {
            Write-Host "Push complete!" -ForegroundColor Green
            Read-Host "Success! Press Enter to exit"
        }
    }
}
