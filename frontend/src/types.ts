export interface User {username:string;is_staff:boolean}
export interface Page<T>{results:T[];count:number;next:string|null;previous:string|null}
export interface Company{id:number;name:string;inn:string;age_months:number}
export interface Product{id:number;name:string;description:string;min_amount:string;max_amount:string;min_term:number;max_term:number;rate:string}
export interface Financial{revenue:string;profit:string;debt:string}
export interface Score{id:number;revision:number;score:number;risk:string;factors:{label:string;points:number}[];stops:string[];explanation:string;recommendation:string}
export interface Decision{id:number;revision:number;outcome:string;reason:string;amount:string|null;term:number|null;rate:string|null}
export interface Application{id:string;company:number;product:number;company_info:Company;product_info:Product;amount:string;term:number;purpose:string;financial:Financial;status:string;revision:number;created_at:string;updated_at:string;history:{id:number;status:string;reason:string;actor:string;created_at:string}[];scores:Score[];decisions:Decision[];verifications:{id:number;provider:string;revision:number;data:Record<string,unknown>}[];documents:{id:number;name:string}[]}
export interface Notification{id:number;application:string;message:string;read:boolean}
