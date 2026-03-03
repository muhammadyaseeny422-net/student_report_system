$filePath = 'c:\Users\user\.antigravity\extensions\syedzawwarahmed.faaaah-1.0.2-universal\media\faah.mp3'
$v = 800
$code = '[DllImport("winmm.dll")] public static extern int mciSendString(string c, string b, int l, IntPtr h);'
$mci = Add-Type -MemberDefinition $code -Name 'MCI' -Namespace 'Win32' -PassThru
$mci::mciSendString("open `"$filePath`" type mpegvideo alias faaah", $null, 0, 0)
$mci::mciSendString("setaudio faaah volume to $v", $null, 0, 0)
$mci::mciSendString("play faaah wait", $null, 0, 0)
$mci::mciSendString("close faaah", $null, 0, 0)
