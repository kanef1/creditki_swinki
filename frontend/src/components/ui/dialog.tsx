import * as DialogPrimitive from '@radix-ui/react-dialog';
import {X} from 'lucide-react';
import type {ReactNode} from 'react';
export const Dialog=DialogPrimitive.Root;
export function DialogContent({title,children}:{title:string;children:ReactNode}) {return <DialogPrimitive.Portal><DialogPrimitive.Overlay className="dialog-overlay"/><DialogPrimitive.Content className="dialog-content"><DialogPrimitive.Title className="text-2xl font-semibold">{title}</DialogPrimitive.Title><DialogPrimitive.Description className="muted">Проверьте данные перед подтверждением.</DialogPrimitive.Description><DialogPrimitive.Close className="dialog-close" aria-label="Закрыть"><X size={20}/></DialogPrimitive.Close>{children}</DialogPrimitive.Content></DialogPrimitive.Portal>}
