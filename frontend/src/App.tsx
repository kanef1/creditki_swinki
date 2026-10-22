import {Children,cloneElement,isValidElement,useEffect,useId,useRef,useState,type ReactElement,type ReactNode} from 'react';
import {useForm} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {ArrowRight,ArrowUpRight,Check,CheckCheck,ChevronDown,Clock3,FileText,LoaderCircle,Package,Plus,ShieldCheck,TrendingUp,Wallet,X} from 'lucide-react';
import {toast} from 'sonner';
import {api,apiUrl} from './api';
import {initializeModule,type ModuleData} from './module-api';
import type {Application,Page,Scenario,Statistics} from './types';
import {JuryScenarios,CompanySelector} from './components/JuryTools';
import {Portfolio,StatisticsStrip} from './components/Portfolio';
import {Button} from './components/ui/button';
import {Input} from './components/ui/input';
import {Dialog,DialogContent} from './components/ui/dialog';
import {Tabs,TabsList,TabsTrigger,TabsContent} from './components/ui/tabs';
import {applicationSchema,defaultForm,date,money,monthlyPayment,statusLabels,type ApplicationForm} from './lib/credit';
export {applicationSchema} from './lib/credit';

const sections=[['product','Продукт'],['terms','Условия'],['application','Заявка'],['result','Результат']] as const;
const icons=[Wallet,TrendingUp,Package];
function scenarioForm(p:Scenario,product=p.product||0):ApplicationForm{return {company:p.company,product,amount:Number(p.amount),term:p.term,purpose:p.purpose,revenue:Number(p.revenue),profit:Number(p.profit),debt:Number(p.debt)}}
function Field({label,help,error,children}:{label:string;help?:string;error?:string;children:ReactNode}){const id=useId();return <div className="field"><label htmlFor={id}>{label}</label>{Children.map(children,(child,i)=>i===0&&isValidElement(child)?cloneElement(child as ReactElement<Record<string,unknown>>,{id,'aria-describedby':help||error?`${id}-hint`:undefined,'aria-invalid':Boolean(error)}):child)}{error?<small id={`${id}-hint`} className="field-error" role="alert">{error}</small>:help?<small id={`${id}-hint`}>{help}</small>:null}</div>}
function Status({value}:{value:string}){return <span className={`status ${['OFFER_READY','COMPLETED'].includes(value)?'positive':['REJECTED','DECLINED'].includes(value)?'negative':''}`}><i/>{statusLabels[value]||value}</span>}
function ErrorBox({message,retry}:{message:string;retry?:()=>void}){return <div className="error-box" role="alert"><p>{message}</p>{retry&&<Button variant="outline" onClick={retry}>Повторить</Button>}</div>}

export default function App(){
  const [data,setData]=useState<ModuleData>();
  const [section,setSection]=useState('product');
  const [application,setApplication]=useState<Application>();
  const [history,setHistory]=useState<Page<Application>>();
  const [historyPage,setHistoryPage]=useState(1);
  const [statistics,setStatistics]=useState<Statistics>();
  const [portfolioVersion,setPortfolioVersion]=useState(0);
  const scenarioKeys=useRef(new Map<string,string>());
  const [error,setError]=useState('');
  const [bootError,setBootError]=useState('');
  const [busy,setBusy]=useState(false);
  const [pending,setPending]=useState<'submit'|'accept'|'decline'|null>(null);
  const [file,setFile]=useState<File>();
  const [loadAttempt,setLoadAttempt]=useState(0);
  const creationKey=useRef(crypto.randomUUID());
  const content=useRef<HTMLDivElement>(null);
  const {register,handleSubmit,watch,reset,setValue,trigger,setError:setFieldError,formState:{errors}}=useForm<ApplicationForm>({resolver:zodResolver(applicationSchema),defaultValues:defaultForm});
  const values=watch();
  const product=data?.products.find(p=>p.id===Number(values.product));
  const company=data?.companies.find(c=>c.id===Number(values.company));
  const editable=!application||['DRAFT','ADDITIONAL_INFO_REQUIRED'].includes(application.status);
  const payment=monthlyPayment(Number(values.amount),Number(values.term),Number(product?.rate||0));

  useEffect(()=>{let active=true;setBootError('');initializeModule().then(result=>{if(!active)return;setData(result);setHistory(result.applications);setStatistics(result.statistics);reset(result.scenarios?.[0]?scenarioForm(result.scenarios[0]):{...defaultForm,company:result.companies[0]?.id||0,product:result.products[0]?.id||0})}).catch(e=>{if(active)setBootError(e.message)});return()=>{active=false}},[reset,loadAttempt]);
  useEffect(()=>{if(section!=='result'||!application||['DRAFT','COMPLETED','DECLINED','REJECTED'].includes(application.status))return;const timer=setInterval(()=>{api<Application>(`applications/${application.id}/`).then(setApplication).catch(()=>{})},10000);return()=>clearInterval(timer)},[section,application?.id,application?.status]);

  function go(next:string){setSection(next);setError('');content.current?.scrollIntoView?.({behavior:'smooth',block:'start'})}
  function fill(app:Application){setApplication(app);setFile(undefined);reset({company:app.company,product:app.product,amount:Number(app.amount),term:app.term,purpose:app.purpose,revenue:Number(app.financial.revenue),profit:Number(app.financial.profit),debt:Number(app.financial.debt)})}
  async function refreshHistory(page=historyPage){const [result,stats]=await Promise.all([api<Page<Application>>(`applications/?page=${page}`),api<Statistics>('applications/statistics/')]);setHistory(result);setStatistics(stats);setHistoryPage(page);setPortfolioVersion(n=>n+1)}
  async function refresh(){if(!application)return;setBusy(true);setError('');try{fill(await api<Application>(`applications/${application.id}/`));await refreshHistory()}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
  function startNew(){setApplication(undefined);creationKey.current=crypto.randomUUID();setFile(undefined);reset(data?.scenarios?.[0]?scenarioForm(data.scenarios[0]):{...defaultForm,company:data?.companies[0]?.id||0,product:data?.products[0]?.id||0});go('product')}
  function chooseCompany(id:number){const profile=data?.scenarios?.find(p=>p.company===id);if(profile)reset(scenarioForm(profile,Number(values.product)));else setValue('company',id)}
  function prefill(profile:Scenario){setApplication(undefined);creationKey.current=crypto.randomUUID();setFile(undefined);reset(scenarioForm(profile));go('application')}
  async function runScenario(profile:Scenario){setBusy(true);setError('');const key=scenarioKeys.current.get(profile.code)||crypto.randomUUID();scenarioKeys.current.set(profile.code,key);try{fill(await api<Application>('demo/scenarios/','POST',{code:profile.code,creation_key:key}));await refreshHistory(1);scenarioKeys.current.delete(profile.code);go('result');toast.success('Сценарий обработан сервером')}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
  async function openApplication(id:string){setBusy(true);setError('');try{fill(await api<Application>(`applications/${id}/`));go('result')}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
  function checkTerms(){if(!product)return false;const amount=Number(values.amount),term=Number(values.term);if(amount<Number(product.min_amount)||amount>Number(product.max_amount)){setFieldError('amount',{message:`От ${money(product.min_amount)} до ${money(product.max_amount)}`});return false}if(term<product.min_term||term>product.max_term){setFieldError('term',{message:`От ${product.min_term} до ${product.max_term} месяцев`});return false}return true}
  async function save(form:ApplicationForm){
    const body={company:form.company,product:form.product,amount:form.amount.toFixed(2),term:form.term,purpose:form.purpose,financial:{revenue:form.revenue.toFixed(2),profit:form.profit.toFixed(2),debt:form.debt.toFixed(2)},...(!application?{creation_key:creationKey.current}:{})};
    let saved=await api<Application>(application?`applications/${application.id}/`:'applications/',application?'PATCH':'POST',body);
    setApplication(saved);
    if(file){const upload=new FormData();upload.append('file',file);await api(`applications/${saved.id}/documents/`,'POST',upload);setFile(undefined);saved=await api<Application>(`applications/${saved.id}/`);setApplication(saved)}
    await refreshHistory(1);return saved;
  }
  async function saveDraft(form:ApplicationForm){if(!checkTerms()){go('terms');return}setBusy(true);setError('');try{const app=await save(form);toast.success('Черновик сохранён');fill(app)}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
  async function confirm(){setBusy(true);setError('');try{if(pending==='submit'){const app=await save(applicationSchema.parse(values));fill(await api<Application>(`applications/${app.id}/submit/`,'POST'));go('result')}else if(application&&pending){fill(await api<Application>(`applications/${application.id}/${pending}/`,'POST'));toast.success(pending==='accept'?'Предложение принято':'Предложение отклонено')}await refreshHistory(1);setPending(null)}catch(e){setError((e as Error).message)}finally{setBusy(false)}}

  const summary=<aside className="calculation" aria-label="Предварительный расчёт"><div className="calculation-label">Ваш расчёт</div><h3>{product?.name||'Выберите продукт'}</h3><div className="payment"><span>Платёж в месяц</span><strong>{Number.isFinite(payment)?money(payment):'—'}</strong></div><dl><div><dt>Сумма</dt><dd>{money(values.amount)}</dd></div><div><dt>Срок</dt><dd>{values.term} мес.</dd></div><div><dt>Ставка в год</dt><dd>{product?.rate||'—'}%</dd></div><div><dt>Всего платежей</dt><dd>{Number.isFinite(payment)?money(payment*Number(values.term)):'—'}</dd></div></dl><p className="fine-print">Предварительный аннуитетный расчёт без комиссий и страховки. Итоговые условия появятся после рассмотрения заявки.</p><div className="secure-note"><ShieldCheck size={18}/><span>Все действия — на этой странице</span></div></aside>;

  return <div className="credit-module">
    <header className="module-header"><div className="header-inner"><button type="button" className="module-brand" onClick={()=>go('product')} aria-label="Кредитование бизнеса"><span className="brand-mark"><TrendingUp size={22}/></span><span>Бизнес<span className="brand-divider">/</span><b>Кредитование</b></span></button><span className="demo-tag">Демонстрационный модуль</span></div></header>
    <main className="module-main">
      <div className="module-intro"><div><span className="eyebrow">ФИНАНСИРОВАНИЕ БИЗНЕСА</span><h1>Кредит под ваши планы</h1><p>Выберите продукт, рассчитайте условия и отправьте заявку.<br className="desktop-break"/> Решение и дальнейшие действия появятся здесь.</p></div><div className="intro-note"><ShieldCheck size={20}/><span>Без визита в офис<br/><b>Всё в одном окне</b></span></div></div>
      {bootError?<ErrorBox message={bootError} retry={()=>setLoadAttempt(n=>n+1)}/>:!data?<div className="loading" role="status"><LoaderCircle className="spin" size={20}/>Подготавливаем кредитный модуль…</div>:
      <Tabs value={section} onValueChange={go} className="module-tabs"><TabsList className="section-nav" aria-label="Разделы кредитного модуля">{sections.map(([id,label],i)=><TabsTrigger key={id} value={id} className="section-tab"><span>{String(i+1).padStart(2,'0')}</span>{label}</TabsTrigger>)}</TabsList>
      <div ref={content} className="module-content">
        {error&&<ErrorBox message={error}/>}
        <TabsContent value="product"><div className="section-title"><div><h2>На что нужны средства?</h2><p>У каждого продукта — своя задача. Выберите подходящий вариант.</p></div>{application&&<Button variant="ghost" onClick={startNew}><Plus size={16}/>Новая заявка</Button>}</div>
          <JuryScenarios scenarios={data.scenarios||[]} busy={busy} onPrefill={prefill} onRun={runScenario}/>
          <div className="product-grid">{data.products.map((p,i)=>{const Icon=icons[i%icons.length];const selected=p.id===Number(values.product);return <button type="button" className={`product-option ${selected?'selected':''}`} aria-pressed={selected} disabled={!editable} key={p.id} onClick={()=>{setValue('product',p.id);setValue('amount',Math.min(Math.max(Number(values.amount),Number(p.min_amount)),Number(p.max_amount)));setValue('term',Math.min(Math.max(Number(values.term),p.min_term),p.max_term))}}><span className="product-top"><span className="product-icon"><Icon size={24}/></span><span className="selection-mark">{selected&&<Check size={14}/>}</span></span><h3>{p.name}</h3><p>{p.description}</p><span className="product-values"><span><small>Сумма до</small><b>{money(p.max_amount)}</b></span><span><small>Ставка</small><b>{p.rate}%</b></span></span><span className="product-duration">До {p.max_term} месяцев<ArrowUpRight size={18}/></span></button>})}</div>
          <div className="section-actions"><p className="fine-print">Условия демонстрационные. Решение зависит от показателей бизнеса.</p><Button onClick={()=>go(editable?'terms':'result')}>{editable?'Рассчитать условия':'Открыть результат'}<ArrowRight size={17}/></Button></div>
          <div className="process-strip"><span><span>1</span>Заполните данные</span><span><span>2</span>Дождитесь проверки</span><span><span>3</span>Получите решение</span></div>
        </TabsContent>
        <TabsContent value="terms"><div className="workspace-grid"><section className="form-panel"><div className="section-title"><div><h2>Подберите комфортные условия</h2><p>{product?.name}. Расчёт меняется вместе с параметрами.</p></div></div><fieldset disabled={busy||!editable}>
          <Field label="Сумма кредита, ₽" error={errors.amount?.message}><Input type="number" step="10000" min={product?.min_amount} max={product?.max_amount} {...register('amount')}/><input className="range" type="range" aria-label="Сумма кредита на шкале" min={product?.min_amount} max={product?.max_amount} step="10000" value={values.amount} onChange={e=>setValue('amount',Number(e.target.value),{shouldValidate:true})}/><span className="range-labels"><span>{money(product?.min_amount||0)}</span><span>{money(product?.max_amount||0)}</span></span></Field>
          <Field label="Срок, месяцев" error={errors.term?.message} help={`От ${product?.min_term} до ${product?.max_term} месяцев`}><Input type="number" min={product?.min_term} max={product?.max_term} {...register('term')}/></Field><div className="term-options">{[6,12,24,36,48,60].filter(t=>t>=(product?.min_term||0)&&t<=(product?.max_term||0)).map(t=><button type="button" key={t} aria-pressed={Number(values.term)===t} className={Number(values.term)===t?'active':''} onClick={()=>setValue('term',t)}>{t} мес.</button>)}</div>
          </fieldset><div className="section-actions"><Button variant="ghost" onClick={()=>go('product')}>Изменить продукт</Button><Button disabled={busy} onClick={async()=>{if(!editable){go('result');return}const valid=await trigger(['amount','term']);if(valid&&checkTerms())go('application')}}>К заявке<ArrowRight size={17}/></Button></div></section>{summary}</div></TabsContent>
        <TabsContent value="application"><div className="workspace-grid"><form className="form-panel" onSubmit={handleSubmit(saveDraft)}><div className="section-title"><div><h2>Расскажите о бизнесе</h2><p>Проверьте компанию и укажите показатели за последние 12 месяцев.</p></div></div><fieldset disabled={busy||!editable}><CompanySelector companies={data.companies} scenarios={data.scenarios||[]} selected={company} disabled={busy||Boolean(application)} onSelect={chooseCompany}/><Field label="Цель финансирования" error={errors.purpose?.message} help="Например, закупка товара для нового сезона"><textarea placeholder="На что планируете направить средства?" {...register('purpose')}/></Field><div className="form-grid">{(['revenue','profit','debt'] as const).map((name,i)=><Field key={name} label={['Годовая выручка, ₽','Годовая прибыль, ₽','Текущий долг, ₽'][i]} error={errors[name]?.message}><Input type="number" step="0.01" {...register(name)}/></Field>)}</div>
          <div className="document-upload"><div><FileText size={20}/><div><b>Документы — при необходимости</b><p>Синтетический PDF до 5 МБ</p></div></div><Input type="file" aria-label="Приложить PDF" accept="application/pdf" onChange={e=>{const selected=e.target.files?.[0];if(selected&&(!selected.name.toLowerCase().endsWith('.pdf')||selected.size>5*1024*1024)){toast.error('Выберите PDF до 5 МБ');e.target.value='';return}setFile(selected)}}/>{file&&<span className="selected-file">{file.name}<button type="button" aria-label="Убрать выбранный файл" onClick={()=>setFile(undefined)}><X size={14}/></button></span>}</div>
          </fieldset><p className="fine-print form-notice">В демонстрации используются только синтетические данные. Проверки ФНС и БКИ выполняются автоматически после отправки.</p><div className="section-actions"><Button type="submit" variant="outline" disabled={busy||!editable}>{busy?'Сохраняем…':'Сохранить черновик'}</Button><Button type="button" disabled={busy} onClick={handleSubmit(()=>{if(!editable){go('result');return}if(!checkTerms()){go('terms');return}setError('');setPending('submit')})}>{editable?'Отправить заявку':'Открыть результат'}<ArrowRight size={17}/></Button></div></form>{summary}</div></TabsContent>
        <TabsContent value="result"><div className="section-title"><div><h2>Ваша заявка</h2><p>Предложение, результаты проверки и история — в одном месте.</p></div><Button variant="outline" onClick={startNew}><Plus size={16}/>Новая заявка</Button></div>
          <StatisticsStrip value={statistics}/>
          {!application&&history?.count?<p className="portfolio-hint">Выберите «Детали» в таблице, чтобы открыть решение, проверки и историю заявки.</p>:!application?<div className="empty-state"><FileText size={32}/><h3>Здесь появится решение</h3><p>Отправьте заявку или откройте сохранённый черновик.</p><Button onClick={()=>go(history?.count?'application':'product')}>Продолжить оформление<ArrowRight size={16}/></Button></div>:<ApplicationResult application={application} busy={busy} onRefresh={refresh} onEdit={()=>go('application')} onRespond={setPending}/>}
          <Portfolio version={portfolioVersion} onOpen={openApplication}/>
        </TabsContent>
      </div></Tabs>}
      <footer className="module-footer"><span>Кредитный модуль для предпринимателя</span><span>Синтетические данные · Без реальной выдачи средств</span></footer>
    </main>
    <Dialog open={pending!==null} onOpenChange={open=>{if(!open&&!busy)setPending(null)}}><DialogContent title={pending==='submit'?'Отправить заявку?':pending==='accept'?'Принять предложение?':'Отклонить предложение?'}><div className="confirmation-copy"><p>{pending==='submit'?`Запрос на ${money(values.amount)} на ${values.term} мес. будет отправлен на проверку.`:pending==='accept'?`Вы принимаете условия на ${money(application?.decisions.at(-1)?.amount||0)}. Демонстрационный процесс будет завершён.`:'Предложение будет отклонено. Это действие сохранится в истории.'}</p>{error&&<ErrorBox message={error}/>}</div><div className="dialog-actions"><Button variant="outline" disabled={busy} onClick={()=>setPending(null)}>Вернуться</Button><Button disabled={busy} onClick={confirm}>{busy?<><LoaderCircle className="spin" size={16}/>Обрабатываем…</>:'Подтвердить'}</Button></div></DialogContent></Dialog>
  </div>;
}

function ApplicationResult({application:a,busy,onRefresh,onEdit,onRespond}:{application:Application;busy:boolean;onRefresh:()=>void;onEdit:()=>void;onRespond:(value:'accept'|'decline')=>void}){
  const decision=a.decisions.at(-1),score=a.scores.at(-1);
  const offer=a.status==='OFFER_READY',complete=a.status==='COMPLETED',rejected=['REJECTED','DECLINED'].includes(a.status),draft=['DRAFT','ADDITIONAL_INFO_REQUIRED'].includes(a.status);
  const Icon=offer||complete?CheckCheck:rejected?FileText:Clock3;
  const title=offer?'Предложение готово':complete?'Предложение принято':a.status==='MANUAL_REVIEW'?'Заявка на рассмотрении':a.status==='ADDITIONAL_INFO_REQUIRED'?'Дополните сведения':a.status==='DRAFT'?'Черновик сохранён':rejected?'Рассмотрение завершено':'Проверяем заявку';
  return <><section className={`result-panel ${offer||complete?'offer':rejected?'rejected':''}`}><div className="result-heading"><span className="result-icon"><Icon size={24}/></span><div><span className="eyebrow">ЗАЯВКА № {a.id.slice(0,8)}</span><h3>{title}</h3></div><Status value={a.status}/></div><p className="result-explanation">{decision?.reason||(draft?'Проверьте данные и отправьте заявку, когда будете готовы.':'Сотрудник изучит показатели бизнеса. Решение появится на этой странице.')}</p><div className="offer-values"><div><span>{decision?.amount?'Предлагаемая сумма':'Запрошенная сумма'}</span><b>{money(decision?.amount||a.amount)}</b></div><div><span>Срок</span><b>{decision?.term||a.term} мес.</b></div>{decision?.rate&&<div><span>Ставка в год</span><b>{decision.rate}%</b></div>}</div>{decision?.amount&&Number(decision.amount)!==Number(a.amount)&&<p className="fine-print">Вы запрашивали {money(a.amount)}. Предлагаемая сумма рассчитана на основании показателей бизнеса.</p>}
    <div className="result-actions">{offer&&<><Button disabled={busy} onClick={()=>onRespond('accept')}>Принять предложение<Check size={17}/></Button><Button variant="ghost" disabled={busy} onClick={()=>onRespond('decline')}>Отклонить</Button></>}{draft&&<Button onClick={onEdit}>Продолжить оформление<ArrowRight size={17}/></Button>}<Button variant="outline" disabled={busy} onClick={onRefresh}>{busy?'Обновляем…':'Обновить статус'}</Button></div>{complete&&<p className="fine-print">Условия приняты. Подписание договора и выдача денег в этом прототипе не выполняются.</p>}</section>
    <div className="result-details"><details><summary>Данные и документы<ChevronDown size={17}/></summary><div className="details-body"><dl className="detail-list"><div><dt>Компания</dt><dd>{a.company_info.name}</dd></div><div><dt>Цель</dt><dd>{a.purpose}</dd></div><div><dt>Выручка за год</dt><dd>{money(a.financial.revenue)}</dd></div><div><dt>Прибыль за год</dt><dd>{money(a.financial.profit)}</dd></div><div><dt>Долг</dt><dd>{money(a.financial.debt)}</dd></div></dl>{a.documents.map(d=><a className="file-link" key={d.id} href={apiUrl(`applications/${a.id}/documents/${d.id}/`)}><FileText size={17}/>{d.name}<ArrowUpRight size={15}/></a>)}</div></details>
    <details><summary>История офферов по заявке<ChevronDown size={17}/></summary><div className="details-body">{a.decisions.filter(d=>d.outcome==='OFFER_READY').length?a.decisions.filter(d=>d.outcome==='OFFER_READY').map(d=><div className="offer-version" key={d.id}><b>Версия {d.revision} · {money(d.amount||0)}</b><span>{d.term} мес. · {d.rate}% годовых</span><p>{d.reason}</p></div>):<p>Предложение ещё не сформировано.</p>}</div></details>
    <details><summary>Как сформировано решение<ChevronDown size={17}/></summary><div className="details-body">{score?<><div className="score-summary"><strong>{score.score}<small>/100</small></strong><span>{({LOW:'Низкий риск',MEDIUM:'Умеренный риск',HIGH:'Высокий риск'} as Record<string,string>)[score.risk]}</span></div><p className="fine-print">{score.explanation}</p><dl className="detail-list">{score.factors.map(f=><div key={f.label}><dt>{f.label}</dt><dd>+{f.points}</dd></div>)}</dl>{score.stops.map(s=><p className="stop-factor" key={s}>{s}</p>)}<p className="fine-print">Выполнены синтетические проверки: {a.verifications.filter(v=>v.revision===a.revision).map(v=>v.provider==='FNS'?'ФНС':'БКИ').join(', ')}. Это демонстрационные правила, а не кредитная политика банка.</p></>:<p>Оценка появится после отправки заявки.</p>}</div></details>
    <details><summary>История заявки<ChevronDown size={17}/></summary><ol className="timeline details-body">{a.history.map(h=><li key={h.id}><span className="timeline-dot"/><div><b>{statusLabels[h.status]}</b><p>{h.reason}</p><small>{date(h.created_at)}</small></div></li>)}</ol></details></div>
  </>;
}
