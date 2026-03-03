$mcisendstring = @"
using System;
using System.Runtime.InteropServices;
public class MCI {
    [DllImport("winmm.dll")]
    public static extern int mciSendString(string command, string buffer, int bufferSize, IntPtr hwndCallback);
}
"@
Add-Type -TypeDefinition $mcisendstring
$filePath = 'c:\Users\user\.antigravity\extensions\syedzawwarahmed.faaaah-1.0.2-universal\media\faah.mp3'
$v = 1000
[MCI]::mciSendString("open `"$filePath`" type mpegvideo alias faaah", $null, 0, [IntPtr]::Zero) | Out-Null
[MCI]::mciSendString("setaudio faaah volume to $v", $null, 0, [IntPtr]::Zero) | Out-Null
[MCI]::mciSendString("play faaah wait", $null, 0, [IntPtr]::Zero) | Out-Null
[MCI]::mciSendString("close faaah", $null, 0, [IntPtr]::Zero) | Out-Null
echo "Done mciSendString"
