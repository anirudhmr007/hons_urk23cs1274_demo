$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open('C:\Users\LENOVO\.gemini\antigravity\scratch\modular_agent\PROJECT_REPORT.docx')
foreach ($p in $doc.Paragraphs) {
    $t = $p.Range.Text.Trim()
    if ($t -like 'CHAPTER*' -or $t -like 'APPENDIX*' -or $t -like 'REFERENCES*') {
        $page = $p.Range.Information(3)
        $clean = $t.Replace("`r", " ").Replace("`n", " ")
        if ($clean.Length -gt 35) { $clean = $clean.Substring(0, 35) }
        Write-Output "$clean -> Page: $page"
    }
}
$doc.Close([ref]$false)
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
