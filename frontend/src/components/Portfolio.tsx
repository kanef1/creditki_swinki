import {useEffect,useState} from 'react';
import {ArrowRight,RefreshCw,Search} from 'lucide-react';
import {api} from '../api';
import type {Application,OfferRecord,Page,Statistics} from '../types';
import {date,money,statusLabels} from '../lib/credit';
import {Button} from './ui/button';
import {Input} from './ui/input';
import {Table} from './ui/table';

export function StatisticsStrip({value}:{value?:Statistics}){
  if(!value||!Number.isFinite(value.total))return null;
  return <div className="portfolio-statistics" aria-label="Статистика заявок">{[
    ['Всего заявок',value.total,''],['Ручное рассмотрение',value.manual,'manual'],['С оффером',value.offers,'approved'],['Отказов банка',value.rejected,'rejected'],['Сумма офферов',money(value.offer_amount),'volume']
  ].map(([label,total,tone])=><div className={`statistic ${tone}`} key={label}><span>{label}</span><strong>{total}</strong></div>)}</div>;
}

export function Portfolio({version,onOpen}:{version:number;onOpen:(id:string)=>void}){
  const [kind,setKind]=useState<'applications'|'offers'>('applications');
  const [status,setStatus]=useState('');const [search,setSearch]=useState('');const [page,setPage]=useState(1);
  const [rows,setRows]=useState<Page<Application|OfferRecord>>();const [loading,setLoading]=useState(false);const [error,setError]=useState('');const [reload,setReload]=useState(0);
  useEffect(()=>{let active=true;const timer=setTimeout(()=>{setLoading(true);setError('');const query=new URLSearchParams({page:String(page),search,status});api<Page<Application|OfferRecord>>(`applications/${kind==='offers'?'offers/':''}?${query}`).then(result=>{if(active)setRows(result)}).catch(e=>{if(active)setError(e.message)}).finally(()=>{if(active)setLoading(false)})},180);return()=>{active=false;clearTimeout(timer)}},[kind,status,search,page,version,reload]);
  function select(next:'applications'|'offers'){setKind(next);setPage(1);setStatus('')}
  return <section className="portfolio-panel"><div className="section-title"><div><h2>Заявки и история офферов</h2><p>Данные всех компаний вашей демо-среды. Статистика учитывает всю историю, включая следующие страницы.</p></div><Button variant="ghost" aria-label="Обновить историю" onClick={()=>setReload(n=>n+1)}><RefreshCw size={17}/></Button></div><div className="portfolio-toolbar"><div className="portfolio-switch"><button type="button" aria-pressed={kind==='applications'} className={kind==='applications'?'active':''} onClick={()=>select('applications')}>Все заявки</button><button type="button" aria-pressed={kind==='offers'} className={kind==='offers'?'active':''} onClick={()=>select('offers')}>История офферов</button></div><label className="portfolio-search"><Search size={16}/><Input aria-label="Поиск по компании или ИНН" placeholder="Компания или ИНН" value={search} onChange={e=>{setSearch(e.target.value);setPage(1)}}/></label><select aria-label="Фильтр статуса истории" value={status} onChange={e=>{setStatus(e.target.value);setPage(1)}}><option value="">Все статусы</option>{(kind==='offers'?['OFFER_READY','COMPLETED','DECLINED']:['DRAFT','MANUAL_REVIEW','ADDITIONAL_INFO_REQUIRED','OFFER_READY','COMPLETED','REJECTED','DECLINED']).map(s=><option key={s} value={s}>{statusLabels[s]}</option>)}</select></div>
    {error?<div className="error-box" role="alert"><p>{error}</p><Button variant="outline" onClick={()=>setReload(n=>n+1)}>Повторить</Button></div>:<><Table aria-label={kind==='offers'?'История офферов':'Список заявок'} aria-busy={loading}><thead><tr><th>{kind==='offers'?'Оффер / дата':'Заявка / дата'}</th><th>Компания / ИНН</th><th>Запрос / предложение</th><th>{kind==='offers'?'Версия':'Скоринг'}</th><th>Статус</th><th/></tr></thead><tbody>{rows?.results.map(row=>{
      const app='company_info' in row?row:undefined,offer='application_status' in row?row:undefined;
      const company=app?.company_info||offer!.company;const id=app?.id||offer!.application;
      const state=app?.status||offer!.application_status;const last=app?.decisions.at(-1);const amount=offer?.amount||last?.amount;const term=offer?.term||last?.term;const rate=offer?.rate||last?.rate;
      return <tr key={row.id}><td><b>№ {String(id).slice(0,8)}</b><small>{date(row.created_at)}</small></td><td><b>{company.name}</b><small>ИНН {company.inn}</small></td><td><b>{money(app?.amount||offer!.requested_amount)}</b>{amount?<small className="offered-amount">→ {money(amount)} · {term} мес. · {rate}%</small>:<small>Оффер пока не сформирован</small>}</td><td>{offer?`№ ${offer.revision}`:app?.scores.at(-1)?.score??'—'}</td><td><span className={`status ${['OFFER_READY','COMPLETED'].includes(state)?'positive':['REJECTED','DECLINED'].includes(state)?'negative':''}`}><i/>{statusLabels[state]}</span></td><td><Button variant="outline" onClick={()=>onOpen(id)}>Детали<ArrowRight size={14}/></Button></td></tr>
    })}{!rows?.results.length&&<tr><td colSpan={6} className="portfolio-empty">{loading?'Загружаем историю…':'По выбранным условиям записей нет'}</td></tr>}</tbody></Table><div className="portfolio-paging"><span>{loading?'Обновляем…':`Всего записей: ${rows?.count??0}`}</span><Button variant="ghost" disabled={!rows?.previous||loading} onClick={()=>setPage(n=>n-1)}>Назад</Button><span>{page}</span><Button variant="ghost" disabled={!rows?.next||loading} onClick={()=>setPage(n=>n+1)}>Далее</Button></div></>}
    <p className="fine-print">«Сумма офферов» — действующие и принятые предложения, а не реальные выдачи. Отклонённые клиентом предложения сохраняются в истории, но не входят в эту сумму.</p>
  </section>;
}
