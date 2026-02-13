const { spawn } = require('child_process');
const path = require('path');

// Mock REPO_ROOT as standard in actual server
const REPO_ROOT = path.resolve(__dirname, '..');

console.log(`[Test] Running health check script from: ${REPO_ROOT}\\scripts\\system_health_check.ps1`);

const ps = spawn('powershell.exe', [
  '-ExecutionPolicy', 'Bypass',
  '-File', path.join(REPO_ROOT, 'scripts', 'system_health_check.ps1')
]);

let stdout = '';
let stderr = '';

ps.stdout.on('data', (data) => {
    console.log(`[Stdout Chunk] ${data.length} bytes`);
    stdout += data.toString();
});
ps.stderr.on('data', (data) => {
    console.log(`[Stderr Chunk] ${data.toString()}`);
    stderr += data.toString();
});

ps.on('close', (code) => {
  console.log(`[Close] Exit Code: ${code}`);
  
  if (stderr) {
      console.warn(`[Warn] Stderr content present: ${stderr}`);
  }

  try {
    const raw = stdout.trim();
    console.log(`[Raw Output] Start:\n${raw.substring(0, 100)}...\nEnd`);
    
    // Attempt parse
    const data = JSON.parse(raw);
    console.log('[Success] JSON Parsed Correctly:');
    console.log(JSON.stringify(data, null, 2));
  } catch (e) {
    console.error(`[Error] JSON Parse Failed: ${e.message}`);
    console.error('Full Output Dump:');
    console.error(stdout);
  }
});
