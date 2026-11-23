import { pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs/promises';
const root = path.join(process.env.LOCALAPPDATA, 'RevitMCP');
const { Client } = await import(pathToFileURL(path.join(root, 'node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js')));
const { StdioClientTransport } = await import(pathToFileURL(path.join(root, 'node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.js')));
const [input, output] = process.argv.slice(2);
if (!input || !output) throw new Error('Usage: revit_call.mjs request.json response.json');
const request = input.endsWith('.cs')
  ? {name:'send_code_to_revit',arguments:{code:await fs.readFile(input,'utf8'),transactionMode:process.argv.includes('--auto')?'auto':'none'}}
  : JSON.parse(await fs.readFile(input, 'utf8'));
if(Buffer.byteLength(JSON.stringify({method:request.name,params:request.arguments}))>7800) throw new Error('Request exceeds the Revit bridge single-read limit');
const transport = new StdioClientTransport({command: path.join(root, 'node-v22.23.2-win-x64/node.exe'), args:[path.join(root, 'node_modules/mcp-server-for-revit/build/index.js')], cwd:root, stderr:'pipe'});
let diagnostics = '';
transport.stderr?.on('data', data => {diagnostics += data.toString();});
const client = new Client({name:'leichhardt-modelling', version:'1.0.0'});
try {
  await client.connect(transport);
  const response = await client.callTool(request, undefined, {timeout:120000});
  await fs.writeFile(output, JSON.stringify({at:new Date().toISOString(),request,response,diagnostics},null,2));
  let result=response;
  const resultText=response.content?.find(c=>c.type==='text')?.text;
  if(request.name==='send_code_to_revit' && resultText?.includes('Result: ')) {
    result=JSON.parse(resultText.split('Result: ')[1]);
    if(result.success && typeof result.result==='string') {
      try {result.result=JSON.parse(result.result);} catch {}
    }
  }
  console.log(JSON.stringify(result,null,2));
  if(response.isError || result.success===false) process.exitCode=1;
} finally {await client.close();}
