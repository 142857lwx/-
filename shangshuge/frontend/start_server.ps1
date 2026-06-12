$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:8888/")
$listener.Start()
Write-Host "Server running on http://localhost:8888"

while ($listener.IsListening) {
    $context = $listener.GetContext()
    $request = $context.Request
    $response = $context.Response
    
    $localPath = $request.Url.LocalPath
    if ($localPath -eq "/") {
        $localPath = "/index.html"
    }
    
    $filePath = Join-Path (Get-Location) $localPath.TrimStart("/")
    
    if (Test-Path $filePath -PathType Leaf) {
        $content = Get-Content $filePath -Raw -Encoding UTF8
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
        $response.ContentLength64 = $bytes.Length
        
        $extension = [System.IO.Path]::GetExtension($filePath).ToLower()
        switch ($extension) {
            ".html" { $response.ContentType = "text/html; charset=UTF-8" }
            ".js" { $response.ContentType = "text/javascript; charset=UTF-8" }
            ".css" { $response.ContentType = "text/css; charset=UTF-8" }
            ".json" { $response.ContentType = "application/json; charset=UTF-8" }
            default { $response.ContentType = "application/octet-stream" }
        }
        
        $response.OutputStream.Write($bytes, 0, $bytes.Length)
    } else {
        $response.StatusCode = 404
        $notFound = [System.Text.Encoding]::UTF8.GetBytes("File not found")
        $response.ContentLength64 = $notFound.Length
        $response.ContentType = "text/plain; charset=UTF-8"
        $response.OutputStream.Write($notFound, 0, $notFound.Length)
    }
    
    $response.Close()
}