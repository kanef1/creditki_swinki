import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { companyApi, applicationApi } from '../../api/client';
import { Company, ApplicationListItem } from '../../types';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { StatusBadge } from '../../components/ui/Badge';
import {
  Building2,
  TrendingUp,
  FileText,
  Clock,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  PlusCircle,
  HelpCircle,
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [company, setCompany] = useState<Company | null>(null);
  const [applications, setApplications] = useState<ApplicationListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [companiesRes, appsRes] = await Promise.all([
          companyApi.list(),
          applicationApi.list(),
        ]);
        if (companiesRes && companiesRes.length > 0) {
          setCompany(companiesRes[0]);
        }
        setApplications(appsRes);
      } catch (err) {
        console.error('Error fetching dashboard data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const latestFin = company?.financial_reports?.[0];
  const activeOfferApp = applications.find((a) => a.status === 'OFFER_READY');

  return (
    <div className="space-y-6">
      {/* Top Banner with Offer Alert if present */}
      {activeOfferApp && (
        <div className="bg-gradient-to-r from-red-600 to-rose-700 text-white rounded-2xl p-5 shadow-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="font-extrabold text-base">Вам доступно кредитное предложение!</div>
              <div className="text-xs text-white/90 mt-0.5">
                По заявке #{activeOfferApp.application_number} банк подготовил персональные условия.
              </div>
            </div>
          </div>
          <Link to={`/applications/${activeOfferApp.id}`}>
            <Button variant="secondary" size="sm" className="bg-white text-alfa-black hover:bg-gray-100 font-bold">
              Посмотреть условия
            </Button>
          </Link>
        </div>
      )}

      {/* Greeting & Company Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-alfa-black tracking-tight">
            Здравствуйте, {user?.first_name || 'Уважаемый клиент'}!
          </h1>
          <p className="text-xs sm:text-sm text-gray-500 mt-1">
            Кредитный кабинет компании{' '}
            <span className="font-semibold text-gray-800">{company?.name || 'ООО / ИП'}</span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/products">
            <Button variant="outline" size="sm" leftIcon={<TrendingUp className="w-4 h-4" />}>
              Кредитный калькулятор
            </Button>
          </Link>
          <Link to="/apply">
            <Button variant="primary" size="sm" leftIcon={<PlusCircle className="w-4 h-4" />}>
              Новая заявка
            </Button>
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <Card className="p-5">
          <div className="flex items-center justify-between text-gray-500 text-xs font-semibold uppercase tracking-wider">
            <span>Компания</span>
            <Building2 className="w-4 h-4 text-alfa-red" />
          </div>
          <div className="mt-2 font-bold text-gray-900 text-sm truncate">
            {company?.short_name || company?.name || 'Загрузка...'}
          </div>
          <div className="text-xs text-gray-500 mt-0.5">ИНН {company?.inn || '—'}</div>
        </Card>

        {/* Metric 2 */}
        <Card className="p-5">
          <div className="flex items-center justify-between text-gray-500 text-xs font-semibold uppercase tracking-wider">
            <span>Годовая выручка</span>
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-2 font-extrabold text-gray-900 text-xl">
            {latestFin ? `${Number(latestFin.annual_revenue).toLocaleString('ru-RU')} ₽` : '—'}
          </div>
          <div className="text-xs text-emerald-600 font-medium mt-0.5">
            Прибыль: {latestFin ? `${Number(latestFin.net_profit).toLocaleString('ru-RU')} ₽` : '—'}
          </div>
        </Card>

        {/* Metric 3 */}
        <Card className="p-5">
          <div className="flex items-center justify-between text-gray-500 text-xs font-semibold uppercase tracking-wider">
            <span>Возраст бизнеса</span>
            <Clock className="w-4 h-4 text-blue-600" />
          </div>
          <div className="mt-2 font-extrabold text-gray-900 text-xl">
            {company ? `${company.business_age_years} г.` : '—'}
          </div>
          <div className="text-xs text-gray-500 mt-0.5">
            Регистрация: {company?.registration_date || '—'}
          </div>
        </Card>

        {/* Metric 4 */}
        <Card className="p-5">
          <div className="flex items-center justify-between text-gray-500 text-xs font-semibold uppercase tracking-wider">
            <span>Всего заявок</span>
            <FileText className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="mt-2 font-extrabold text-gray-900 text-xl">{applications.length}</div>
          <div className="text-xs text-gray-500 mt-0.5">
            Активных: {applications.filter((a) => a.status !== 'COMPLETED' && a.status !== 'REJECTED').length}
          </div>
        </Card>
      </div>

      {/* Main Grid: Applications & Company Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Active Applications */}
        <div className="lg:col-span-8 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-gray-900 tracking-tight">Ваши кредитные заявки</h2>
            <Link to="/history" className="text-xs text-alfa-red font-semibold hover:underline">
              Все заявки →
            </Link>
          </div>

          {applications.length === 0 ? (
            <Card className="p-8 text-center">
              <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <div className="font-bold text-gray-800 text-base">У вас пока нет оформленных заявок</div>
              <p className="text-xs text-gray-500 max-w-sm mx-auto mt-1 mb-4">
                Выберите кредитный продукт и заполните простую форму для получения решения онлайн за 2 минуты.
              </p>
              <Link to="/apply">
                <Button variant="primary" size="sm">
                  Оформить первую заявку
                </Button>
              </Link>
            </Card>
          ) : (
            <div className="space-y-3">
              {applications.map((app) => (
                <Card
                  key={app.id}
                  className="p-4 sm:p-5 hover:border-gray-300 hover:shadow-sm transition-all"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-gray-500">
                          #{app.application_number}
                        </span>
                        <StatusBadge status={app.status} label={app.status_display} />
                      </div>
                      <div className="text-base font-bold text-gray-900 mt-1">
                        {app.product_name}
                      </div>
                      <div className="text-xs text-gray-500 mt-0.5">
                        Цель: {app.purpose || 'Пополнение оборотных средств'}
                      </div>
                    </div>

                    <div className="flex items-center justify-between sm:justify-end gap-6 border-t sm:border-t-0 pt-3 sm:pt-0 border-gray-100">
                      <div className="text-left sm:text-right">
                        <div className="text-xs text-gray-400 font-semibold uppercase">Сумма</div>
                        <div className="text-sm font-extrabold text-gray-900">
                          {Number(app.requested_amount).toLocaleString('ru-RU')} ₽
                        </div>
                        <div className="text-[11px] text-gray-500">{app.term_months} мес.</div>
                      </div>

                      <Link to={`/applications/${app.id}`}>
                        <Button variant="outline" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                          Детали
                        </Button>
                      </Link>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Right: Company Profile & Fast Calculator CTA */}
        <div className="lg:col-span-4 space-y-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" />
                Реквизиты организации
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-3 space-y-3 text-xs">
              <div>
                <span className="text-gray-400 block font-medium">Наименование:</span>
                <span className="font-semibold text-gray-800">{company?.name || '—'}</span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <span className="text-gray-400 block font-medium">ИНН:</span>
                  <span className="font-mono font-semibold text-gray-800">{company?.inn || '—'}</span>
                </div>
                <div>
                  <span className="text-gray-400 block font-medium">ОГРН:</span>
                  <span className="font-mono font-semibold text-gray-800">{company?.ogrn || '—'}</span>
                </div>
              </div>
              <div>
                <span className="text-gray-400 block font-medium">Руководитель:</span>
                <span className="font-semibold text-gray-800">{company?.ceo_name || '—'}</span>
              </div>
              <div>
                <span className="text-gray-400 block font-medium">ОКВЭД:</span>
                <span className="font-semibold text-gray-800">
                  {company?.okved} {company?.okved_description ? `(${company.okved_description})` : ''}
                </span>
              </div>
              <div>
                <span className="text-gray-400 block font-medium">Юридический адрес:</span>
                <span className="text-gray-700">{company?.legal_address || '—'}</span>
              </div>
            </CardContent>
          </Card>

          {/* Alfa Help Note */}
          <div className="bg-red-50 border border-red-100 rounded-2xl p-4 text-xs">
            <div className="flex items-start gap-2.5">
              <HelpCircle className="w-4 h-4 text-alfa-red flex-shrink-0 mt-0.5" />
              <div>
                <div className="font-bold text-gray-900">Как работает умный конвейер?</div>
                <div className="text-gray-600 mt-1 leading-relaxed">
                  После отправки заявки система автоматически запрашивает данные ФНС и БКИ, выполняет скоринг и формирует персональное предложение в течение 1 минуты.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
