let csrf='';
export class ApiError extends Error {constructor(public status:number,message:string){super(message)}}
function describe(value:unknown):string {if(typeof value==='string')return value;if(Array.isArray(value))return value.map(describe).join('; ');if(value&&typeof value==='object')return Object.entries(value).map(([k,v])=>`${k}: ${describe(v)}`).join('; ');return String(value)}
export async function api<T>(path:string,method='GET',data?:unknown):Promise<T>{
  if(!csrf&&method!=='GET'){const response=await fetch('/api/v1/auth/csrf/',{credentials:'same-origin'});if(!response.ok)throw new ApiError(response.status,'Не удалось установить защищённое соединение');csrf=(await response.json()).csrfToken}
  const headers:Record<string,string>={};if(method!=='GET')headers['X-CSRFToken']=csrf;if(data&&!(data instanceof FormData))headers['Content-Type']='application/json';
  let response:Response;try{response=await fetch(`/api/v1/${path}`,{method,credentials:'same-origin',headers,body:data instanceof FormData?data:data?JSON.stringify(data):undefined})}catch{throw new ApiError(0,'Нет соединения с сервером. Повторите попытку.')}
  const body=await response.json().catch(()=>({}));if(!response.ok){if(response.status===403)csrf='';throw new ApiError(response.status,describe(body.error?.details||(response.status===403?'Не удалось проверить сессию. Обновите страницу и повторите вход.':'Ошибка сервера')))}
  if(path==='auth/login/'||path==='auth/logout/')csrf='';return body as T;
}
