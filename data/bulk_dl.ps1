$urls = Get-Content "5354632352-download.txt"

foreach($url in $urls){
	Start-Process $url
}s