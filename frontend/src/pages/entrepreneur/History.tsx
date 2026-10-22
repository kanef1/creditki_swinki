import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { applicationApi } from '../../api/client';
import { ApplicationListItem } from '../../types';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { StatusBadge } from '../../components/ui/Badge';
import { FileText, Search, ArrowRight, PlusCircle, Filter } from 'lucide-react';

export const History: React.FC = () => {
  const [applications, setApplications] = useState<ApplicationListItem[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    applicationApi
      .list()
      .then((data) => setApplications(data))
      .finally(() => setLoading(false));
  }, []);

  const filtered = applications.filter((app) => {
    if (filterStatus === 'ACTIVE') {
      if (['COMPLETED', 'REJECTED', 'DRAFT'].includes(app.status)) return false;
    } else if (filterStatus === 'DECIDED') {
      if (!['OFFER_READY', 'ACCEPTED', 'COMPLETED', 'REJECTED'].includes(app.status)) return false;
    } else if (filterStatus === 'DRAFT') {
      if (app.status !== 'DRAFT') return false;
    }

    if (search.trim()) {
      const q = search.toLowerCase();
      const matchNum = app.application_number.toLowerCase().includes(q);
      const matchProd = app.product_name.toLowerCase().includes(q);
      return matchNum || matchProd;
    }

    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-alfa-black tracking-tight">
            История кредитных заявок
          </h1>
          <p className="text-xs sm:text-sm text-gray-500 mt-1">
            Отслеживайте движение заявок по кредитному конвейеру в реальном времени.
          </p>
        </div>
        <Link to="/apply">
          <Button variant="primary" size="sm" leftIcon={<PlusCircle className="w-4 h-4" />}>
            Новая заявка
          </Button>
        </Link>
      </div>

      {/* Filters and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Status Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {[
            { id: 'ALL', label: 'Все заявки' },
            { id: 'ACTIVE', label: 'В процессе' },
            { id: 'DECIDED', label: 'С решением' },
            { id: 'DRAFT', label: 'Черновики' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilterStatus(tab.id)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
                filterStatus === tab.id
                  ? 'bg-alfa-black text-white shadow-sm'
                  : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Номер заявки или продукт..."
            className="w-full pl-9 pr-3 py-2 bg-white border border-gray-200 rounded-xl text-xs focus:outline-none focus:border-alfa-red"
          />
        </div>
      </div>

      {/* Applications List */}
      {loading ? (
        <div className="text-center py-12 text-xs text-gray-400">Загрузка заявок...</div>
      ) : filtered.length === 0 ? (
        <Card className="p-12 text-center">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <div className="text-base font-bold text-gray-700">Заявок не найдено</div>
          <p className="text-xs text-gray-400 mt-1">Попробуйте изменить параметры поиска или фильтрации.</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {filtered.map((app) => (
            <Card
              key={app.id}
              className="p-5 hover:border-gray-300 hover:shadow-sm transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-gray-500">
                    #{app.application_number}
                  </span>
                  <StatusBadge status={app.status} label={app.status_display} />
                </div>
                <div className="text-base font-bold text-gray-900 mt-1">{app.product_name}</div>
                <div className="text-xs text-gray-500 mt-0.5">
                  Компания: <span className="font-medium text-gray-700">{app.company_name}</span> (ИНН{' '}
                  {app.company_inn})
                </div>
              </div>

              <div className="flex items-center justify-between sm:justify-end gap-6 border-t sm:border-t-0 pt-3 sm:pt-0 border-gray-100">
                <div className="text-left sm:text-right">
                  <div className="text-xs text-gray-400 font-semibold uppercase">Сумма</div>
                  <div className="text-base font-extrabold text-gray-900">
                    {Number(app.requested_amount).toLocaleString('ru-RU')} ₽
                  </div>
                  <div className="text-[11px] text-gray-500">Срок: {app.term_months} мес.</div>
                </div>

                <Link to={`/applications/${app.id}`}>
                  <Button variant="outline" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                    Перейти
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
