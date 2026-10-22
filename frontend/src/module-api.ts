import {api} from './api';
import type {Application,Company,Page,Product} from './types';
export interface ModuleData {companies:Company[];products:Product[];applications:Page<Application>}
let initialization:Promise<ModuleData>|undefined;
export function initializeModule(){
  if(!initialization)initialization=(async()=>{
    await api('context/','POST');
    const [companies,products,applications]=await Promise.all([api<Page<Company>>('companies/'),api<Page<Product>>('products/'),api<Page<Application>>('applications/')]);
    return {companies:companies.results,products:products.results,applications};
  })().catch(error=>{initialization=undefined;throw error});
  return initialization;
}
