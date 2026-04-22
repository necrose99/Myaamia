# runspider.ps1
$SpiderFile = "ilda-master.py"
$MediaDir = "C:\Users\black\GitHub\Myaamia\corpus_media"

# Ensure the media directory exists
if (!(Test-Path $MediaDir)) { New-Item -ItemType Directory -Path $MediaDir }

# Run Scrapy with properly escaped JSON for PowerShell
scrapy runspider $SpiderFile `
    -s ITEM_PIPELINES='{"__main__.AlgicMediaPipeline": 1}' `
    -s FILES_STORE=$MediaDir `
    -s FILES_EXPIRES=90 `
    -s RETRY_TIMES=5 `
    -o mirror_results.json