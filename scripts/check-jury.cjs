const assert=require('node:assert/strict');
const base=process.env.APP_URL||'http://127.0.0.1:8080';
function session(){const jar={};return async(path,method='GET',body,status=200)=>{
  const r=await fetch(base+'/api/v1/'+path,{method,headers:{Origin:new URL(base).origin,Cookie:Object.entries(jar).map(([k,v])=>`${k}=${v}`).join('; '),'X-CSRFToken':jar.csrftoken||'','Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});for(const v of r.headers.getSetCookie()){const [k,value]=v.split(';')[0].split('=');jar[k]=value;}const text=await r.text();assert.equal(r.status,status,`${path}: ${text.slice(0,180)}`);return JSON.parse(text);
}}
(async()=>{
  const one=session(),two=session();
  for(const request of [one,two]){await request('auth/csrf/');await request('context/','POST');await request('auth/csrf/');}
  const profiles=(await one('demo/scenarios/')).results;assert.equal(profiles.length,4);assert.equal(new Set(profiles.map(p=>p.company)).size,4);
  const statistics=await one('applications/statistics/');assert.deepEqual(statistics,{total:4,manual:1,offers:2,rejected:1,accepted:0,offer_amount:'9500000.00'});
  const apps=(await one('applications/')).results;
  for(const p of profiles){const app=apps.find(a=>a.company===p.company);assert.equal(app.status,p.expected_status);assert.equal(app.verifications.length,2);assert.equal(app.scores.length,1);}
  const key=crypto.randomUUID();const input={code:'counter',creation_key:key};const app=await one('demo/scenarios/','POST',input);assert.equal(app.decisions.at(-1).amount,'4500000.00');assert.equal((await one('demo/scenarios/','POST',input)).id,app.id);
  assert.equal((await one('applications/statistics/')).total,5);
  await one(`applications/${app.id}/decline/`,'POST');
  assert.equal((await one('applications/statistics/')).offer_amount,'9500000.00');
  const history=await one('applications/offers/');assert.equal(history.count,3);assert.equal(history.results.find(o=>o.application===app.id).application_status,'DECLINED');
  assert.equal((await one('applications/offers/?status=DECLINED')).count,1);
  await two(`applications/${app.id}/`,'GET',undefined,404);
  assert.equal((await two('applications/statistics/')).total,4);
  console.log('Jury HTTP: 4 private companies, all outcomes, computed statistics, idempotent replay, offer history, filters and visitor isolation passed.');
})().catch(e=>{console.error(e.message);process.exitCode=1});
