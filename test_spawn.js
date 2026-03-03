const { spawn } = require('child_process');
const filePath = 'c:\\Users\\user\\.antigravity\\extensions\\syedzawwarahmed.faaaah-1.0.2-universal\\media\\faah.mp3';
const v = 1000;
const script = `$c = '[DllImport("winmm.dll")] public static extern int mciSendString(string c, string b, int l, IntPtr h);'; $m = Add-Type -MemberDefinition $c -Name 'M' -Namespace 'W' -PassThru; $m::mciSendString('open ""${filePath}"" type mpegvideo alias f', $null, 0, 0); $m::mciSendString('setaudio f volume to ${v}', $null, 0, 0); $m::mciSendString('play f wait', $null, 0, 0); $m::mciSendString('close f', $null, 0, 0);`;
console.log("Script:", script);
const ps = spawn("powershell", ["-WindowStyle", "Hidden", "-NoProfile", "-Command", script], { detached: true, stdio: "ignore" });
ps.unref();
console.log("Spawned");
