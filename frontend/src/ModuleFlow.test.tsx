import {afterEach,expect,it,vi} from 'vitest';
import {cleanup,fireEvent,render,screen} from '@testing-library/react';
import App from './App';
import {initializeModule} from './module-api';
vi.mock('./module-api',()=>({initializeModule:vi.fn()}));
afterEach(()=>{cleanup();vi.unstubAllGlobals()});

it('submits and accepts an offer inside the four-section module',async()=>{
  const company={id:1,name:'Синтетическая компания',inn:'990000000001',age_months:48};
  const product={id:1,name:'Оборотные средства',description:'Для текущих расходов',min_amount:'100000',max_amount:'5000000',min_term:6,max_term:36,rate:'19.50'};
  const draft={id:'synthetic-id',company:1,product:1,company_info:company,product_info:product,amount:'1000000.00',term:24,purpose:'Закупка синтетического оборудования',financial:{revenue:'12000000.00',profit:'2400000.00',debt:'1000000.00'},status:'DRAFT',revision:0,created_at:'2026-10-22T10:00:00Z',updated_at:'2026-10-22T10:00:00Z',history:[],scores:[],decisions:[],verifications:[],documents:[]};
  const offer={...draft,status:'OFFER_READY',decisions:[{id:1,revision:1,outcome:'OFFER_READY',reason:'Показатели соответствуют условиям модели',amount:'1000000.00',term:24,rate:'19.50'}]};
  vi.mocked(initializeModule).mockResolvedValue({companies:[company],products:[product],applications:{count:0,next:null,previous:null,results:[]}});
  const fetchMock=vi.fn(async(input:string,options?:RequestInit)=>{
    const body=input.endsWith('auth/csrf/')?{csrfToken:'synthetic-csrf'}:input.endsWith('/submit/')?offer:input.endsWith('/accept/')?{...offer,status:'COMPLETED'}:options?.method==='POST'?draft:{count:1,next:null,previous:null,results:[draft]};
    return {ok:true,status:200,json:async()=>body};
  });
  vi.stubGlobal('fetch',fetchMock);
  render(<App/>);
  await screen.findByRole('heading',{name:'На что нужны средства?'});
  fireEvent.mouseDown(screen.getByRole('tab',{name:/Заявка/}),{button:0,ctrlKey:false});
  fireEvent.change(screen.getByLabelText('Цель финансирования'),{target:{value:'Закупка синтетического оборудования'}});
  fireEvent.click(screen.getByRole('button',{name:'Отправить заявку'}));
  await screen.findByRole('dialog');
  fireEvent.click(screen.getByRole('button',{name:'Подтвердить'}));
  await screen.findByRole('heading',{name:'Предложение готово'});
  expect(screen.getByRole('tab',{name:/Результат/})).toHaveAttribute('aria-selected','true');
  fireEvent.click(screen.getByRole('button',{name:'Принять предложение'}));
  await screen.findByRole('dialog');
  fireEvent.click(screen.getByRole('button',{name:'Подтвердить'}));
  await screen.findByRole('heading',{name:'Предложение принято'});
  expect(screen.getAllByRole('tab')).toHaveLength(4);
  expect(fetchMock.mock.calls.some(([path])=>path.includes('auth/login'))).toBe(false);
});
