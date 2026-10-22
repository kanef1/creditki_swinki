import {describe,it,expect,vi,afterEach} from 'vitest';
import {render,screen,fireEvent,waitFor,cleanup} from '@testing-library/react';
import {BrowserRouter} from 'react-router-dom';
import App,{applicationSchema} from './App';
import {api} from './api';
afterEach(()=>{cleanup();vi.unstubAllGlobals()});
describe('credit form',()=>{it('rejects inconsistent profit and negative debt',()=>{expect(applicationSchema.safeParse({company:1,product:1,amount:100000,term:12,purpose:'Закупка товаров',revenue:100,profit:200,debt:-1}).success).toBe(false)});it('accepts consistent financial data',()=>{expect(applicationSchema.safeParse({company:1,product:1,amount:100000,term:12,purpose:'Закупка товаров',revenue:100,profit:20,debt:0}).success).toBe(true)});it('shows login validation',async()=>{vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,status:403,json:async()=>({})}));render(<BrowserRouter><App/></BrowserRouter>);await screen.findByText('Войти в кабинет');fireEvent.click(screen.getByRole('button',{name:'Войти'}));await waitFor(()=>expect(screen.getByText('Введите пароль')).toBeInTheDocument())})});
describe('API errors',()=>{it('reports network failure',async()=>{vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new Error('offline')));await expect(api('products/')).rejects.toThrow('Нет соединения')});it('reports server validation',async()=>{vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,status:400,json:async()=>({error:{details:{amount:['Сумма вне диапазона']}}})}));await expect(api('products/')).rejects.toThrow('Сумма вне диапазона')})});
