import test from 'node:test';
import assert from 'node:assert/strict';
import { createHmac, generateKeyPairSync, verify } from 'node:crypto';
import {makeHandler} from '../src/github-app.mjs';
const keys=generateKeyPairSync('rsa',{modulusLength:2048});
const env={GITHUB_APP_ID:'123',GITHUB_APP_WEBHOOK_SECRET:'synthetic-test-key',GITHUB_APP_PRIVATE_KEY:keys.privateKey.export({type:'pkcs1',format:'pem'})};
const repo='ChongLiuPhil/Personal-Publishing-Framework';
const registry=[{repository:repo,branch:'main'}];
const base={repository:{full_name:repo,private:false,default_branch:'main'},ref:'refs/heads/main',after:'a'.repeat(40),installation:{id:42}};
function request(payload=base, event='push', signature=true){
 const body=JSON.stringify(payload);
 return new Request('https://example.com/_events/github',{method:'POST',body,headers:{'x-github-event':event,'x-hub-signature-256':signature?'sha256='+createHmac('sha256',env.GITHUB_APP_WEBHOOK_SECRET).update(body).digest('hex'):'sha256='+'0'.repeat(64)}});
}
test('fail closed when secrets are absent or signature is wrong',async()=>{
 const handle=makeHandler(registry,()=>assert.fail('network'));
 assert.equal((await handle(request(),{})).status,503);
 assert.equal((await handle(request(base,'push',false),env)).status,401);
 assert.equal((await handle(request(base,'ping'),env)).status,200);
});
test('reject unregistered/private/drifted sources and ignore non-default and self pushes',async()=>{
 const handle=makeHandler(registry,()=>assert.fail('network'));
 for(const [payload,expected] of [[{...base,repository:{...base.repository,full_name:'other/repo'}},403],[{...base,repository:{...base.repository,private:true}},403],[{...base,ref:'refs/heads/topic'},202],[{...base,deleted:true},202],[{...base,repository:{...base.repository,full_name:'ChongLiuPhil/Inquiry-Publishing-Project-Starter'}},202],[{...base,ref:'refs/heads/new',repository:{...base.repository,default_branch:'new'}},409],[{...base,after:'main'},400]]){
  assert.equal((await handle(request(payload),env)).status,expected);
 }
});
test('mint only Starter Actions write token, verify JWT, dispatch immutable identity',async()=>{
 const calls=[];
 const handle=makeHandler(registry,async(url,options)=>{
  calls.push({url,options});
  if(calls.length===1){
   const jwt=options.headers.Authorization.slice(7); const [head,body,sig]=jwt.split('.');
   assert.equal(verify('RSA-SHA256',Buffer.from(head+'.'+body),keys.publicKey,Buffer.from(sig,'base64url')),true);
   const claims=JSON.parse(Buffer.from(body,'base64url'));assert.equal(claims.iss,'123');assert.ok(claims.exp-claims.iat<=600);
   assert.deepEqual(JSON.parse(options.body),{repositories:['Inquiry-Publishing-Project-Starter'],permissions:{actions:'write'}});
   return Response.json({token:'synthetic-installation-token'},{status:201});
  }
  assert.deepEqual(JSON.parse(options.body),{ref:'main',inputs:{repository:repo,branch:'main',revision:base.after}});
  return new Response(null,{status:204});
 });
 const result=await handle(request(),env);assert.equal(result.status,202);assert.equal(calls.length,2);
 assert.match(await result.text(),/subject to validation/);
});
test('upstream errors never echo credentials or payloads',async()=>{
 for(const mode of ['throw','denied','dispatch']){
  let count=0;
  const handle=makeHandler(registry,async()=>{
   count++; if(mode==='throw')throw new Error(env.GITHUB_APP_PRIVATE_KEY);
   if(mode==='denied'||count===2)return new Response(env.GITHUB_APP_PRIVATE_KEY,{status:403});
   return Response.json({token:'synthetic'},{status:201});
  });
  const result=await handle(request(),env);assert.equal(result.status,502);assert.ok(!(await result.text()).includes('PRIVATE KEY'));
 }
});
test('oversized body is refused before external calls',async()=>{
 const result=await makeHandler(registry,()=>assert.fail('network'))(new Request('https://example.com/_events/github',{method:'POST',body:'x',headers:{'content-length':String(3*1024*1024)}}),env);
 assert.equal(result.status,413);
});

test('workerd runtime supports PEM signing and WebCrypto verification',async()=>{
 const {Miniflare,convertV4MiniflareOptions}=await import('miniflare');
 const {readFileSync}=await import('node:fs');
 const runtime=new Miniflare(convertV4MiniflareOptions({workers:[{
  name:"webhook-test",compatibilityDate:'2026-09-22',compatibilityFlags:['nodejs_compat'],
  modules:true,
  script:readFileSync(new URL('../src/github-app.mjs',import.meta.url),'utf8').replaceAll('export ', '')+`
    let calls=0;
    export default {fetch:makeHandler(${JSON.stringify(registry)},async()=>++calls===1?Response.json({token:'synthetic'},{status:201}):new Response(null,{status:204}))};`,
  bindings:env,
 }]}));
 try{
  const req=request();
  const result=await runtime.dispatchFetch(req.url,{method:req.method,headers:Object.fromEntries(req.headers),body:await req.text()});
  assert.equal(result.status,202,await result.text());
 }finally{await runtime.dispose();}
});


test('PEM formatting variants preserve key identity; invalid keys fail without network or disclosure',async()=>{
 for(const type of ['pkcs1','pkcs8']){
  const pem=keys.privateKey.export({type,format:'pem'});
  for(const value of [pem,pem.replaceAll('\n',''),pem.replaceAll('\n','\\n'),pem.replaceAll('\n','\r\n')]){
   let count=0;
   const handle=makeHandler(registry,async(_url,options)=>{
    if(++count===1){
     const [head,body,sig]=options.headers.Authorization.slice(7).split('.');
     assert.ok(verify('RSA-SHA256',Buffer.from(head+'.'+body),keys.publicKey,Buffer.from(sig,'base64url')));
     return Response.json({token:'synthetic'},{status:201});
    }
    return new Response(null,{status:204});
   });
   assert.equal((await handle(request(),{...env,GITHUB_APP_PRIVATE_KEY:value})).status,202);
  }
 }
 const handle=makeHandler(registry,()=>assert.fail('network'));
 const result=await handle(request(),{...env,GITHUB_APP_PRIVATE_KEY:'synthetic-invalid-secret'});
 assert.equal(result.status,502);const message=await result.text();
 assert.match(message,/key signing failed/);assert.ok(!message.includes('synthetic-invalid-secret'));
});
