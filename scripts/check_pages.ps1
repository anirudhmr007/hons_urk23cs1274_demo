$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("C:\Users\LENOVO\.gemini\antigravity\scratch\modular_agent\PROJECT_REPORT.docx")
$pages = $doc.ComputeStatistics(2)
$doc.Close([ref]$false)
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
Write-Output "TOTAL_PAGES:$pages"
