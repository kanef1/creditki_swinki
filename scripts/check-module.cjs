const assert=require('node:assert/strict');
const base=process.env.APP_URL||'http://127.0.0.1:8080';
function visitor(){const cookies={};return async(path,method='GET',body,expected=200)=>{
  const response=await fetch(base+'/api/v1/'+path,{method,headers:{Origin:new URL(base).origin,Cookie:Object.entries(cookies).map(([k,v])=>`${k}=${v}`).join('; '),'X-CSRFToken':cookies.csrftoken||'','Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});
  for(const cookie of response.headers.getSetCookie()){const [k,v]=cookie.split(';')[0].split('=');cookies[k]=v;}
  const text=await response.text();assert.equal(response.status,expected,`${method} ${path}: ${text.slice(0,200)}`);return JSON.parse(text);
}}
(async()=>{
  const one=visitor(),two=visitor();
  for(const request of [one,two]){await request('auth/csrf/');await request('context/','POST');await request('auth/csrf/');}
  const company=(await one('companies/')).results[0];
  const otherCompany=(await two('companies/')).results[0];assert.notEqual(company.id,otherCompany.id);
  const product=(await one('products/')).results[0];
  const key=crypto.randomUUID();
  const app=await one('applications/','POST',{company:company.id,product:product.id,creation_key:key,amount:'1000000.00',term:24,purpose:'Синтетическая закупка оборудования для проверки модуля',financial:{revenue:'12000000.00',profit:'2400000.00',debt:'1000000.00'}},201);
  const path=`applications/${app.id}/`;
  assert.equal((await one(path,'PATCH',{purpose:'Обновлённая синтетическая закупка оборудования'})).status,'DRAFT');
  const result=await one(path+'submit/','POST');assert.equal(result.status,'OFFER_READY');assert.equal(result.verifications.length,2);assert.equal(result.scores.length,1);
  await two(path,'GET',undefined,404);
  assert.equal((await one(path+'accept/','POST')).status,'COMPLETED');
  await one('context/','POST');assert.equal((await one(path)).status,'COMPLETED');
  console.log('Module: no login, private visitor context, draft/edit/submit/checks/scoring/offer/accept/reload OK.');
})().catch(error=>{console.error(error.message);process.exitCode=1});
