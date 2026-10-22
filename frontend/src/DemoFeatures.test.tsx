import {afterEach,expect,it,vi} from 'vitest';
import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {JuryScenarios,CompanySelector} from './components/JuryTools';
import {Portfolio,StatisticsStrip} from './components/Portfolio';
import type {Scenario} from './types';
afterEach(()=>{cleanup();vi.unstubAllGlobals()});
const profiles:Scenario[]=['approve','counter','manual','reject'].map((code,i)=>({code,title:['Одобрение','Встречная сумма','Рассмотрение','Отказ'][i],name:`Компания ${i+1}`,description:'Синтетические показатели',expected:'Вычисленный результат',expected_status:'OFFER_READY',expected_amount:'1000000.00',company:i+1,inn:`99000000000${i+1}`,product:1,rate:'19.50',age_months:48,credit_score:820,tax_debt:'0.00',overdue_days:0,revenue:'12000000.00',profit:'2400000.00',debt:'1000000.00',amount:'1000000.00',term:24,purpose:'Синтетическое оборудование'}));

it('shows server statistics and labels the amount as offers',()=>{
  render(<StatisticsStrip value={{total:26,manual:1,offers:24,rejected:1,accepted:0,offer_amount:'119500000.00'}}/>);
  expect(screen.getByText('26')).toBeInTheDocument();expect(screen.getByText('24')).toBeInTheDocument();expect(screen.getByText('Сумма офферов')).toBeInTheDocument();expect(screen.queryByText('Объём выдач')).not.toBeInTheDocument();
});

it('provides four jury scenarios and passes the selected profile to actions',()=>{
  const run=vi.fn(),prefill=vi.fn();render(<JuryScenarios scenarios={profiles} busy={false} onPrefill={prefill} onRun={run}/>);
  fireEvent.click(screen.getByText('Сценарии для жюри'));
  const buttons=screen.getAllByRole('button',{name:'Запустить'});expect(buttons).toHaveLength(4);fireEvent.click(buttons[1]);expect(run).toHaveBeenCalledWith(profiles[1]);
  fireEvent.click(screen.getAllByRole('button',{name:'Подставить данные'})[2]);expect(prefill).toHaveBeenCalledWith(profiles[2]);
});

it('finds a private demo company by INN and rejects an unknown company',()=>{
  const select=vi.fn();const companies=profiles.map(p=>({id:p.company,name:p.name,inn:p.inn,age_months:p.age_months,credit_score:p.credit_score}));
  render(<CompanySelector companies={companies} scenarios={profiles} selected={companies[0]} disabled={false} onSelect={select}/>);
  fireEvent.change(screen.getByLabelText('ИНН компании или предпринимателя'),{target:{value:profiles[2].inn}});fireEvent.click(screen.getByRole('button',{name:'Найти'}));expect(select).toHaveBeenCalledWith(3);
  fireEvent.change(screen.getByLabelText('ИНН компании или предпринимателя'),{target:{value:'990000000099'}});fireEvent.click(screen.getByRole('button',{name:'Найти'}));expect(screen.getByRole('alert')).toHaveTextContent('не найден');
});

it('loads offer history with status filtering and opens the associated application',async()=>{
  const open=vi.fn();const fetchMock=vi.fn(async(input:string)=>({ok:true,status:200,json:async()=>input.includes('/offers/')?{count:1,next:null,previous:null,results:[{id:9,application:'offer-app',revision:2,amount:'4500000.00',term:24,rate:'19.50',reason:'Встречная сумма',created_at:'2026-10-22T10:00:00Z',company:{id:2,name:'Компания с оффером',inn:'990000000002',age_months:36},product_name:'Оборотные средства',application_status:'DECLINED',requested_amount:'5000000.00'}]}:{count:0,next:null,previous:null,results:[]}}));vi.stubGlobal('fetch',fetchMock);
  render(<Portfolio version={0} onOpen={open}/>);fireEvent.click(screen.getByRole('button',{name:'История офферов'}));await screen.findByText('Компания с оффером');
  fireEvent.click(screen.getByRole('button',{name:'Детали'}));expect(open).toHaveBeenCalledWith('offer-app');
  fireEvent.change(screen.getByLabelText('Фильтр статуса истории'),{target:{value:'DECLINED'}});
  await waitFor(()=>expect(fetchMock.mock.calls.some(([url])=>url.includes('offers/')&&url.includes('status=DECLINED'))).toBe(true));
});
