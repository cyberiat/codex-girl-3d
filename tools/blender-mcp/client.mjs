import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { createInterface } from 'node:readline';

// Real MCP stdio client. All scene changes run through the installed Blender MCP server.
const request = JSON.parse(readFileSync(process.argv[2], 'utf8').replace(/^\uFEFF/, ''));
if (request.codeFile) {
  request.params = { name: 'execute_blender_code', arguments: { code: readFileSync(request.codeFile, 'utf8'), user_prompt: '模型动作太僵硬了，且动作幅度太小。我在assets里又放了一个更精细的模型，已打开blender，在blender里给模型增加更精细的动作，不要用python直接去操作glb文件。blender有mcp，安装blender mcp然后直接通过mcp操作blender，不要用computer-use了' } };
}
const child = spawn('C:/Users/renat/.local/bin/uvx.exe', ['mcp-for-blender==2.1.9'], {
  env: { ...process.env, DISABLE_TELEMETRY: 'true', BLENDER_HOST: '127.0.0.1', BLENDER_PORT: '9876' },
  windowsHide: true, stdio: ['pipe', 'pipe', 'pipe']
});
let nextId = 1;
const pending = new Map();
let logs = '';
child.stderr.on('data', b => { logs += b; });
const lines = createInterface({ input: child.stdout });
lines.on('line', line => {
  try {
    const msg = JSON.parse(line);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
    }
  } catch {}
});
function send(method, params = {}) {
  const id = nextId++;
  const promise = new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
  child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
  return promise;
}
const timeout = setTimeout(() => {
  console.error('MCP client timeout', logs.slice(-4000)); child.kill(); process.exit(2);
}, request.timeoutMs || 180000);
try {
  const init = await send('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'gpt-dragon-workspace', version: '1.0.0' } });
  child.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) + '\n');
  let result = await send(request.method || 'tools/call', request.params || {});
  if (request.output) writeFileSync(request.output, JSON.stringify(result, null, 2));
  if (request.imagePrefix && result.content) {
    let i = 0;
    result = { ...result, content: result.content.map(c => {
      if (c.type !== 'image') return c;
      const file = `${request.imagePrefix}-${i++}.${c.mimeType === 'image/jpeg' ? 'jpg' : 'png'}`;
      writeFileSync(file, Buffer.from(c.data, 'base64'));
      return { type: 'saved_image', path: file };
    }) };
  }
  if (result.structuredContent && result.content) delete result.structuredContent;
  console.log(JSON.stringify({ server: init.serverInfo, result }, null, 2));
} catch (e) {
  console.error(String(e), logs.slice(-4000)); process.exitCode = 1;
} finally { clearTimeout(timeout); child.stdin.end(); child.kill(); }
