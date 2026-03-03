Add-Type -AssemblyName PresentationCore
$player = New-Object System.Windows.Media.MediaPlayer
$player.Open('c:\Users\user\.antigravity\extensions\syedzawwarahmed.faaaah-1.0.2-universal\media\faah.mp3')
$player.Volume = 1.0
$player.Play()
Start-Sleep -Seconds 3
echo "Done"
