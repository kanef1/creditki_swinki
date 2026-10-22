import type {Score} from '../types';

const levels:Record<string,{label:string;description:string}>={
  LOW:{label:'Низкий',description:'Финансовые показатели соответствуют условиям автоматического одобрения.'},
  MEDIUM:{label:'Умеренный',description:'Перед одобрением требуется дополнительная оценка сотрудником.'},
  HIGH:{label:'Высокий',description:'Выявлены стоп-факторы или недостаточный скоринговый балл.'},
};

export function RiskSummary({score}:{score?:Score}){
  const level=score&&levels[score.risk];
  return <section className={`risk-summary risk-${score?.risk.toLowerCase()||'pending'}`} aria-label="Риск при одобрении"><div className="risk-heading"><div><span className="context-label">Риск при одобрении</span><h4>{level?.label||'Ещё не оценён'}</h4></div>{score&&<strong>{score.score}<small> / 100 баллов</small></strong>}</div><p>{level?.description||'Оценка появится после отправки заявки и выполнения скоринга.'}</p>{score&&<><p className="fine-print">Скоринговый балл показывает оценку по демо-правилам и не является процентом вероятности одобрения.</p>{score.stops.length>0&&<ul>{score.stops.map(stop=><li key={stop}>{stop}</li>)}</ul>}</>}</section>;
}
