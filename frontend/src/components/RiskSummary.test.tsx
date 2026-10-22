import {afterEach,expect,it} from 'vitest';
import {cleanup,render,screen} from '@testing-library/react';
import {RiskSummary} from './RiskSummary';

afterEach(cleanup);
it('shows stop factors even when the score alone appears sufficient',()=>{
  render(<RiskSummary score={{id:1,revision:1,score:85,risk:'HIGH',stops:['Значительная налоговая задолженность'],factors:[],explanation:'Стоп-фактор',recommendation:'REJECT'}}/>);
  expect(screen.getByRole('heading',{name:'Высокий'})).toBeInTheDocument();
  expect(screen.getByText('Значительная налоговая задолженность')).toBeInTheDocument();
  expect(screen.getByText(/не является процентом/)).toBeInTheDocument();
});
it('does not invent a risk before scoring',()=>{
  render(<RiskSummary/>);
  expect(screen.getByRole('heading',{name:'Ещё не оценён'})).toBeInTheDocument();
  expect(screen.queryByText(/100 баллов/)).not.toBeInTheDocument();
});
