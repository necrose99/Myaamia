# Configuration
$inputFile  = "ilda_full.csv"
$outputFile = "ilda_full_fr.csv"
$apiUrl     = "http://127.0.0.1:5050/translate"
$batchSize  = 30

Write-Host "Reading $inputFile..." -ForegroundColor Cyan
$csvData = Import-Csv -Path$inputFile

$total =$csvData.Count
$processed = 0

for ($i = 0; $i -lt$total; $i +=$batchSize) {
    $endIndex = [Math]::Min($i + $batchSize - 1,$total - 1)
    $batch =$csvData[$i..$endIndex]

    # Join lines with newlines into a single string payload
    $joinedText = ($batch.'en-us') -join "`n"

    $payload = @{
        q        = $joinedText
        source   = "en"
        target   = "fr"
        format   = "text"
        api_key  = ""
    } | ConvertTo-Json -Depth 3 -Compress

    try {
        $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Body $payload -ContentType "application/json"
        
        # Split translated response back into individual items
        $translations = $response.translatedText -split "`n"

        for ($j = 0; $j -lt $batch.Count; $j++) {
            $row =$batch[$j]$translated = if ($j -lt$translations.Count) { $translations[$j] } else { "" }

            [PSCustomObject]@{
                mia     = $row.mia
                'en-us' = $row.'en-us'
                fro     = $translated
            } | Export-Csv -Path $outputFile -Append -NoTypeInformation -Encoding UTF8
        }

        $processed +=$batch.Count
        Write-Host "Processed $processed / $total rows..." -ForegroundColor Green

    } catch {
        Write-Host "Error processing batch starting at index $i :$_" -ForegroundColor Red
    }
}

Write-Host "Done! Output saved to $outputFile" -ForegroundColor Yellow