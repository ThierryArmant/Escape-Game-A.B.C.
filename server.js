import http from 'node:http';
import {randomBytes} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {initial,apply,view} from './game.js';
const sessions=new Map();const token=()=>randomBytes(24).toString('hex');
function json(res,status,data){res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(JSON.stringify(data))}
async function body(req){let b='';for await(const chunk of req){b+=chunk;if(b.length>4096)throw Error('Requête trop grande')}return JSON.parse(b||'{}')}
export const server=http.createServer(async(req,res)=>{try{
 const url=new URL(req.url,'http://localhost');
 if(req.method==='POST'&&url.pathname==='/api/sessions'){if(sessions.size>=100)throw Error('Nombre maximal de sessions atteint');let code;do{code=randomBytes(3).toString('hex').toUpperCase()}while(sessions.has(code));const master=token();sessions.set(code,{state:initial(),tokens:{master},created:Date.now()});return json(res,201,{code,token:master,role:'master'})}
 const match=url.pathname.match(/^\/api\/sessions\/([A-F0-9]{6})(?:\/(join|action))?$/);
 if(match){const session=sessions.get(match[1]);if(!session)return json(res,404,{error:'Session introuvable'});
 if(match[2]==='join'&&req.method==='POST'){const {role}=await body(req);if(!['students','manager','supplier'].includes(role))throw Error('Équipe inconnue');session.tokens[role]??=token();return json(res,200,{code:match[1],role,token:session.tokens[role]})}
 const auth=req.headers.authorization?.replace(/^Bearer /,'');const role=Object.keys(session.tokens).find(r=>session.tokens[r]===auth);if(!role)return json(res,403,{error:'Accès refusé'});
 if(!match[2]&&req.method==='GET')return json(res,200,view(session.state));
 if(match[2]==='action'&&req.method==='POST'){const next=structuredClone(session.state);apply(next,role,await body(req));session.state=next;return json(res,200,view(next))}
 }
 if(req.method==='GET'&&['/','/app.js','/style.css'].includes(url.pathname)){const path=url.pathname==='/'?'index.html':url.pathname.slice(1);res.writeHead(200,{'Content-Type':path.endsWith('.html')?'text/html; charset=utf-8':path.endsWith('.js')?'text/javascript; charset=utf-8':'text/css; charset=utf-8','X-Content-Type-Options':'nosniff'});return res.end(await readFile(new URL('./public/'+path,import.meta.url)))}
 json(res,404,{error:'Adresse inconnue'});
 }catch(e){json(res,400,{error:e.message})}});
const cleanup=setInterval(()=>{for(const [code,s]of sessions)if(Date.now()-s.created>8*3600000)sessions.delete(code)},60000);cleanup.unref();
if(process.argv[1]===new URL(import.meta.url).pathname)server.listen(Number(process.env.PORT||3000),'0.0.0.0',()=>console.log('Escape Game A.B.C. : port '+(process.env.PORT||3000)));
