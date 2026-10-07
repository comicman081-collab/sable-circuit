import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(process.argv[2],'utf8');
if(/<script\b[^>]*\bsrc\s*=/i.test(html)||/<link\b[^>]*rel=["']stylesheet/i.test(html))throw Error('External script or stylesheet dependency');
const scripts=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)];
if(!scripts.length)throw Error('No embedded runtime');
for(const [index,match]of scripts.entries())new vm.Script(match[1],{filename:`embedded-${index}.js`});
console.log(JSON.stringify({status:'PASS_SYNTAX',scripts:scripts.length,scope:'JavaScript parse and static dependency tags, not browser behavior'}));
