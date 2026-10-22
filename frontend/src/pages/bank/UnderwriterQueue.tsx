import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { applicationApi } from '../../api/client';
import { ApplicationListItem } from '../../types';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { StatusBadge, Badge } from '../../components/ui/Badge';
import {
  ShieldCheck,
  Search,
  Filter,
  ArrowRight,
  Clock,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  FileText,
  UserCheck,
} from 'lucide-react';

export const UnderwriterQueue: React.FC = () => {
  const navigate = useNavigate();
  const [applications, setApplications] = useState<ApplicationListItem[]>([]);
  const [counts, setCounts] = useState<{
    total: number;
    manual_review: number;
    additional_info: number;
    offer_ready: number;
    completed: number;
    rejected: number;
    drafts: number;
  }>({
    total: 0,
    manual_review: 0,
    additional_info: 0,
    offer_ready: 0,
    completed: 0,
    rejected: 0,
    drafts: 0,
  });
  const [statusGroup, setStatusGroup] = useState<string>('review');
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  const fetchQueue = async () => {
    setLoading(true);
    try {
      const res = await applicationApi.getQueue(statusGroup);
      setCounts(res.counts);
      setApplications(res.applications);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, [statusGroup]);

  const filteredApps = applications.filter((app) => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return (
      app.application_number.toLowerCase().includes(q) ||
      app.company_name.toLowerCase().includes(q) ||
      app.company_inn.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-alfa-red mb-1">
            <ShieldCheck className="w-4 h-4" />
            Рабочее место кредитного офицера
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-alfa-black tracking-tight">
            Очередь кредитного андеррайтинга
          </h1>
          <p className="text-xs sm:text-sm text-gray-500 mt-1">
            Рассмотрение заявок, требующих экспертной оценки, встречные условия и аудит рисков.
          </p>
        </div>
      </div>

      {/* Stats Counter Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
        <div
          onClick={() => setStatusGroup('review')}
          className={`p-3.5 rounded-2xl border cursor-pointer transition-all ${
            statusGroup === 'review'
              ? 'border-amber-500 bg-amber-50/50 shadow-sm'
              : 'border-gray-200 bg-white hover:border-gray-300'
          }`}
        >
          <div className="text-[11px] font-semibold text-amber-700 uppercase">На рассмотрении</div>
          <div className="text-2xl font-extrabold text-amber-900 mt-1">
            {counts.manual_review + counts.additional_info}
          </div>
        </div>

        <div
          onClick={() => setStatusGroup('all')}
          className={`p-3.5 rounded-2xl border cursor-pointer transition-all ${
            statusGroup === 'all'
              ? 'border-alfa-red bg-red-50/50 shadow-sm'
              : 'border-gray-200 bg-white hover:border-gray-300'
          }`}
        >
          <div className="text-[11px] font-semibold text-gray-500 uppercase">Всего заявок</div>
          <div className="text-2xl font-extrabold text-alfa-black mt-1">{counts.total}</div>
        </div>

        <div className="p-3.5 rounded-2xl border border-gray-200 bg-white">
          <div className="text-[11px] font-semibold text-emerald-700 uppercase">Оффер готов</div>
          <div className="text-2xl font-extrabold text-emerald-900 mt-1">{counts.offer_ready}</div>
        </div>

        <div className="p-3.5 rounded-2xl border border-gray-200 bg-white">
          <div className="text-[11px] font-semibold text-emerald-700 uppercase">Выдано</div>
          <div className="text-2xl font-extrabold text-emerald-900 mt-1">{counts.completed}</div>
        </div>

        <div className="p-3.5 rounded-2xl border border-gray-200 bg-white">
          <div className="text-[11px] font-semibold text-rose-700 uppercase">Отказы</div>
          <div className="text-2xl font-extrabold text-rose-900 mt-1">{counts.rejected}</div>
        </div>

        <div className="p-3.5 rounded-2xl border border-gray-200 bg-white">
          <div className="text-[11px] font-semibold text-gray-400 uppercase">Черновики</div>
          <div className="text-2xl font-extrabold text-gray-600 mt-1">{counts.drafts}</div>
        </div>
      </div>

      {/* Tabs & Search */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="flex items-center gap-1.5 overflow-x-auto">
          {[
            { id: 'review', label: 'Требуют решения андеррайтера' },
            { id: 'active', label: 'В работе конвейера' },
            { id: 'all', label: 'Все заявки' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setStatusGroup(tab.id)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
                statusGroup === tab.id
                  ? 'bg-alfa-red text-white shadow-sm'
                  : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Поиск по номеру, названию, ИНН..."
            className="w-full pl-9 pr-3 py-2 bg-white border border-gray-200 rounded-xl text-xs focus:outline-none focus:border-alfa-red"
          />
        </div>
      </div>

      {/* Queue Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50/70 border-b border-gray-200 text-gray-500 font-semibold uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Заявка</th>
                <th className="py-3 px-4">Организация / ИНН</th>
                <th className="py-3 px-4">Продукт</th>
                <th className="py-3 px-4">Запрос</th>
                <th className="py-3 px-4">Скоринг / Риск</th>
                <th className="py-3 px-4">Статус</th>
                <th className="py-3 px-4 text-right">Действие</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-gray-400">
                    Загрузка очереди...
                  </td>
                </tr>
              ) : filteredApps.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-gray-400">
                    В данной группе нет заявок
                  </td>
                </tr>
              ) : (
                filteredApps.map((app) => (
                  <tr key={app.id} className="hover:bg-gray-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-gray-900">
                      {app.application_number}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-gray-900">{app.company_name}</div>
                      <div className="text-gray-400 font-mono text-[11px]">ИНН {app.company_inn}</div>
                    </td>
                    <td className="py-3.5 px-4 text-gray-700">{app.product_name}</td>
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-gray-900">
                        {Number(app.requested_amount).toLocaleString('ru-RU')} ₽
                      </div>
                      <div className="text-gray-400 text-[11px]">{app.term_months} мес.</div>
                    </td>
                    <td className="py-3.5 px-4">
                      {app.scoring_score !== null ? (
                        <div className="flex items-center gap-1.5">
                          <span
                            className={`font-mono font-bold px-2 py-0.5 rounded text-xs ${
                              app.scoring_score >= 75
                                ? 'bg-emerald-50 text-emerald-700'
                                : app.scoring_score >= 45
                                ? 'bg-amber-50 text-amber-700'
                                : 'bg-rose-50 text-rose-700'
                            }`}
                          >
                            {app.scoring_score}/100
                          </span>
                          <span className="text-gray-400 text-[11px] font-medium">
                            {app.risk_level || ''}
                          </span>
                        </div>
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={app.status} label={app.status_display} />
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link to={`/bank/applications/${app.id}`}>
                        <Button
                          variant={app.status === 'MANUAL_REVIEW' ? 'primary' : 'outline'}
                          size="sm"
                          rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                        >
                          {app.status === 'MANUAL_REVIEW' ? 'Рассмотреть' : 'Досье'}
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
