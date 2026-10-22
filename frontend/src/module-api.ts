import {api} from './api';
import type {Application,Company,Page,Product,Statistics,Scenario} from './types';
export interface ModuleData {companies:Company[];products:Product[];applications:Page<Application>;statistics?:Statistics;scenarios?:Scenario[]}
let initialization:Promise<ModuleData>|undefined;
export function initializeModule(){
  if(!initialization)initialization=(async()=>{
    await api('context/','POST');
    const [companies,products,applications,statistics,scenarios]=await Promise.all([api<Page<Company>>('companies/'),api<Page<Product>>('products/'),api<Page<Application>>('applications/'),api<Statistics>('applications/statistics/'),api<{results:Scenario[]}>('demo/scenarios/')]);
    return {companies:companies.results,products:products.results,applications,statistics,scenarios:scenarios.results};
  })().catch(error=>{initialization=undefined;throw error});
  return initialization;
}
