import React from 'react';
import { clsx } from 'clsx';
import { ApplicationStatus } from '../../types';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'neutral' | 'alfa';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral', className }) => {
  const styles = {
    default: 'bg-gray-100 text-gray-800 border-gray-200',
    neutral: 'bg-slate-100 text-slate-700 border-slate-200',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200 font-medium',
    warning: 'bg-amber-50 text-amber-700 border-amber-200 font-medium',
    danger: 'bg-rose-50 text-rose-700 border-rose-200 font-medium',
    info: 'bg-blue-50 text-blue-700 border-blue-200 font-medium',
    alfa: 'bg-red-50 text-alfa-red border-red-200 font-semibold',
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs border font-medium transition-colors',
        styles[variant],
        className
      )}
    >
      {children}
    </span>
  );
};

export const StatusBadge: React.FC<{ status: ApplicationStatus | string; label?: string }> = ({
  status,
  label,
}) => {
  const map: Record<string, { variant: BadgeProps['variant']; defaultLabel: string }> = {
    DRAFT: { variant: 'neutral', defaultLabel: 'Черновик' },
    SUBMITTED: { variant: 'info', defaultLabel: 'Отправлена' },
    VALIDATING: { variant: 'info', defaultLabel: 'Проверка данных' },
    ENRICHING: { variant: 'info', defaultLabel: 'Обогащение (ФНС/БКИ)' },
    SCORING: { variant: 'info', defaultLabel: 'Скоринг' },
    OFFER_READY: { variant: 'success', defaultLabel: 'Предложение готово' },
    MANUAL_REVIEW: { variant: 'warning', defaultLabel: 'На рассмотрении андеррайтера' },
    ADDITIONAL_INFO_REQUIRED: { variant: 'warning', defaultLabel: 'Требуются сведения' },
    ACCEPTED: { variant: 'success', defaultLabel: 'Принято клиентом' },
    COMPLETED: { variant: 'success', defaultLabel: 'Выдано / Договор' },
    REJECTED: { variant: 'danger', defaultLabel: 'Отказано' },
  };

  const config = map[status] || { variant: 'neutral', defaultLabel: status };

  return <Badge variant={config.variant}>{label || config.defaultLabel}</Badge>;
};
