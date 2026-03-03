$player = New-Object -ComObject WMPlayer.OCX
$player.settings.volume = 100
$player.URL = 'c:\Users\user\.antigravity\extensions\syedzawwarahmed.faaaah-1.0.2-universal\media\faah.mp3'
$player.controls.play()

$timeout = 50
while ($player.playState -ne 1 -and $player.playState -ne 8 -and $timeout -gt 0) {
    Start-Sleep -Milliseconds 100
    $timeout--
}
echo "State after loop: $($player.playState)"
