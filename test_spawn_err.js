const { spawn } = require('child_process');
const filePath = 'c:\\Users\\user\\.antigravity\\extensions\\syedzawwarahmed.faaaah-1.0.2-universal\\media\\faah.mp3';
const v = 1000;
const script = `$c = '[DllImport("winmm.dll")] public static extern int mciSendString(string c, string b, int l, IntPtr h);'; $m = Add-Type -MemberDefinition $c -Name 'M' -Namespace 'W' -PassThru; $err1 = $m::mciSendString('open "${filePath}" type mpegvideo alias f', $null, 0, 0); $err2 = $m::mciSendString('setaudio f volume to ${v}', $null, 0, 0); $err3 = $m::mciSendString('play f wait', $null, 0, 0); $m::mciSendString('close f', $null, 0, 0); echo "Codes: $err1 $err2 $err3"`;
const ps = spawn("powershell", ["-NoProfile", "-Command", script]);
ps.stdout.on('data', d => console.log("OUT:", d.toString()));
ps.stderr.on('data', d => console.log("ERR:", d.toString()));
ps.on('close', c => console.log("Done", c));
