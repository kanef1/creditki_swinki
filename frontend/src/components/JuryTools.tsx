import {useState} from 'react';
import {ArrowRight,Building2,Check,ChevronDown,FlaskConical,Search} from 'lucide-react';
import type {Company,Scenario} from '../types';
import {money} from '../lib/credit';
import {Button} from './ui/button';
import {Input} from './ui/input';

export function JuryScenarios({scenarios,busy,onPrefill,onRun}:{scenarios:Scenario[];busy:boolean;onPrefill:(p:Scenario)=>void;onRun:(p:Scenario)=>void}){
  if(!scenarios.length)return null;
  return <details className="jury-panel"><summary><span><FlaskConical size={18}/>Сценарии для жюри<span className="jury-count">4 компании</span></span><ChevronDown size={18}/></summary><div className="jury-content"><p className="fine-print">Четыре исходные заявки уже подготовлены в разделе «Результат». Повторный запуск создаёт новую заявку и выполняет проверки и скоринг на сервере.</p><div className="jury-grid">{scenarios.map((p,i)=><article className={`scenario-card scenario-${p.code}`} key={p.code}><span className="scenario-badge">Сценарий {i+1} · {p.title}</span><h3>{p.name}</h3><span className="scenario-inn">ИНН {p.inn}</span><p className="scenario-description">{p.description}</p><dl className="scenario-metrics"><div><dt>Выручка за {Math.min(p.age_months,12)} мес.</dt><dd>{money(p.revenue)}</dd></div><div><dt>Прибыль за {Math.min(p.age_months,12)} мес.</dt><dd>{money(p.profit)}</dd></div><div><dt>БКИ</dt><dd>{p.credit_score} / 850</dd></div><div><dt>Возраст</dt><dd>{p.age_months} мес.</dd></div></dl><div className="scenario-expected"><b>Ожидаемый результат</b><p>{p.expected}</p></div><div className="scenario-actions"><Button variant="ghost" disabled={busy} onClick={()=>onPrefill(p)}>Подставить данные</Button><Button disabled={busy} onClick={()=>onRun(p)}>Запустить<ArrowRight size={15}/></Button></div></article>)}</div></div></details>;
}

export function CompanySelector({companies,scenarios,selected,disabled,onSelect}:{companies:Company[];scenarios:Scenario[];selected?:Company;disabled:boolean;onSelect:(id:number)=>void}){
  const [inn,setInn]=useState('');const [error,setError]=useState('');
  const profile=scenarios.find(p=>p.company===selected?.id);
  const financial=selected?.financial_snapshot||profile;
  const period=Math.min(selected?.age_months||12,12);
  function find(){const value=inn.replace(/\s/g,'');if(!/^\d{10}(\d{2})?$/.test(value)){setError('Введите синтетический ИНН из 10 или 12 цифр');return}const company=companies.find(c=>c.inn===value);if(!company){setError('Этот ИНН не найден в вашей демо-среде. Выберите компанию ниже.');return}setError('');onSelect(company.id)}
  return <div className="company-selector">
    <label htmlFor="company-inn">ИНН компании или предпринимателя</label>
    <div className="company-search"><Search size={18}/><Input id="company-inn" inputMode="numeric" placeholder={selected?.inn||'10 или 12 цифр'} value={inn} disabled={disabled} onChange={e=>{setInn(e.target.value);setError('')}} onKeyDown={e=>{if(e.key==='Enter'){e.preventDefault();find()}}}/><Button type="button" variant="outline" disabled={disabled} onClick={find}>Найти</Button></div>
    {error&&<p className="field-error" role="alert">{error}</p>}
    <div className="company-chips" aria-label="Демонстрационные компании">{companies.map(c=>{
      const active=selected?.id===c.id;
      return <button type="button" key={c.id} aria-label={c.name} disabled={disabled} className={active?'selected':''} aria-pressed={active} onClick={()=>{setInn(c.inn);setError('');onSelect(c.id)}}><span className="company-choice-top"><Building2 size={19} aria-hidden="true"/><span className="company-choice-check">{active&&<Check size={13} aria-hidden="true"/>}</span></span><b>{c.name}</b><small>{c.age_months} мес. работы</small></button>;
    })}</div>
    <div className="company-context company-profile"><div className="company-profile-heading"><span className="company-profile-icon"><Building2 size={24}/></span><div><span className="context-label">Выбранная компания</span><h3>{selected?.name}</h3><p>ИНН {selected?.inn} <span>·</span> {selected?.age_months} мес. работы</p></div><span className="company-profile-tag">{profile?'Демо-профиль':'Данные кабинета'}</span></div>
      {selected&&<dl className="company-facts">{financial?<><div><dt>Выручка за {period} мес.</dt><dd>{money(financial.revenue)}</dd></div><div><dt>Прибыль за {period} мес.</dt><dd className={Number(financial.profit)<0?'fact-negative':'fact-positive'}>{money(financial.profit)}</dd></div><div><dt>Текущий долг</dt><dd>{money(financial.debt)}</dd></div></>:<div><dt>Финансовые показатели</dt><dd>Нет данных — укажите в заявке</dd></div>}<div><dt>Рейтинг БКИ</dt><dd>{selected.credit_score??'—'}<small> / 850</small></dd></div><div><dt>Долг ФНС</dt><dd className={Number(selected.tax_debt)>0?'fact-negative':''}>{money(selected.tax_debt||0)}</dd></div><div><dt>Просрочка</dt><dd className={selected.overdue_days?'fact-negative':''}>{selected.overdue_days??0} дней</dd></div></dl>}
    </div>
    {disabled&&<p className="fine-print">Компания сохранённой заявки не меняется. Для другой компании создайте новую заявку.</p>}
  </div>;
}
