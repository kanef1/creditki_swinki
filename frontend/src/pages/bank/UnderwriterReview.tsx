import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { applicationApi, decisionApi, documentApi } from '../../api/client';
import { ApplicationDetail, CreditDecision } from '../../types';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { StatusBadge, Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import {
  ShieldCheck,
  Building2,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  FileText,
  Clock,
  ArrowLeft,
  Scale,
  Send,
  HelpCircle,
} from 'lucide-react';

export const UnderwriterReview: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [app, setApp] = useState<ApplicationDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);

  // Decision Form State
  const [isDecisionModalOpen, setIsDecisionModalOpen] = useState(false);
  const [decisionTab, setDecisionTab] = useState<
    'APPROVED' | 'COUNTER_OFFER' | 'ADDITIONAL_INFO_REQUIRED' | 'REJECTED'
  >('APPROVED');
  const [approvedAmount, setApprovedAmount] = useState<number>(0);
  const [approvedTerm, setApprovedTerm] = useState<number>(0);
  const [approvedRate, setApprovedRate] = useState<number>(0);
  const [decisionNotes, setDecisionNotes] = useState<string>('');
  const [rejectionReasons, setRejectionReasons] = useState<string>('');

  const fetchApp = async () => {
    if (!id) return;
    try {
      const data = await applicationApi.get(Number(id));
      setApp(data);
      setApprovedAmount(Number(data.requested_amount));
      setApprovedTerm(data.term_months);
      setApprovedRate(Number(data.product.base_rate));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApp();
  }, [id]);

  const handleApplyDecision = async () => {
    if (!id) return;
    setActionLoading(true);
    try {
      const reasonsList = rejectionReasons
        ? rejectionReasons.split('\n').filter((r) => r.trim().length > 0)
        : [];

      await decisionApi.applyManual(Number(id), {
        decision_type: decisionTab,
        approved_amount: approvedAmount,
        approved_term_months: approvedTerm,
        approved_rate: approvedRate,
        notes: decisionNotes,
        reasons: reasonsList,
      });

      setIsDecisionModalOpen(false);
      await fetchApp();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12 text-sm text-gray-400">Загрузка досье андеррайтера...</div>;
  }

  if (!app) {
    return <div className="text-center py-12 text-sm text-gray-400">Заявка не найдена</div>;
  }

  const scoring = app.scoring_result;
  const decision = app.decision;
  const latestFin = app.company?.financial_reports?.[0];

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb & Action Header */}
      <div>
        <Link
          to="/bank"
          className="text-xs text-alfa-red hover:underline font-semibold flex items-center gap-1 mb-2"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Назад к очереди андеррайтинга
        </Link>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-gray-200 shadow-sm">
          <div>
            <div className="flex items-center gap-3">
              <span className="font-mono text-sm font-extrabold text-alfa-red">
                #{app.application_number}
              </span>
              <StatusBadge status={app.status} label={app.status_display} />
              {scoring && (
                <span
                  className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
                    scoring.score >= 75
                      ? 'bg-emerald-50 text-emerald-700'
                      : scoring.score >= 45
                      ? 'bg-amber-50 text-amber-700'
                      : 'bg-rose-50 text-rose-700'
                  }`}
                >
                  Скоринг: {scoring.score}/100
                </span>
              )}
            </div>
            <h1 className="text-xl sm:text-2xl font-extrabold text-alfa-black mt-1">
              {app.company?.name}
            </h1>
            <p className="text-xs text-gray-500 mt-0.5">
              ИНН {app.company?.inn} · Руководитель: {app.company?.ceo_name} · Заявитель: {app.applicant_name}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="primary"
              size="md"
              onClick={() => setIsDecisionModalOpen(true)}
              leftIcon={<ShieldCheck className="w-4 h-4" />}
              className="font-bold shadow"
            >
              Принять решение андеррайтера
            </Button>
          </div>
        </div>
      </div>

      {/* Decision Summary if already made */}
      {decision && (
        <Card className="border-l-4 border-l-alfa-red p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <div className="text-xs font-bold uppercase tracking-wider text-gray-400">
                Текущее решение по заявке
              </div>
              <div className="text-base font-bold text-gray-900 mt-0.5 flex items-center gap-2">
                <span>{decision.decision_type_display}</span>
                <span className="text-xs font-normal text-gray-500">
                  ({decision.is_automated ? 'Автоматическое' : `Принято: ${decision.decided_by_name}`})
                </span>
              </div>
              <div className="text-xs text-gray-700 mt-1">{decision.rationale}</div>
            </div>

            {Number(decision.approved_amount) > 0 && (
              <div className="text-right sm:border-l sm:pl-6 border-gray-100 flex-shrink-0">
                <div className="text-xs text-gray-400">Утвержденная сумма</div>
                <div className="text-lg font-extrabold text-alfa-black">
                  {Number(decision.approved_amount).toLocaleString('ru-RU')} ₽
                </div>
                <div className="text-xs text-gray-500">
                  {decision.approved_term_months} мес. · {decision.approved_rate}%
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Dossier Grid: 3 Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Col 1: Financial indicators */}
        <div className="lg:col-span-4 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-600" />
                Финансовый профиль
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div>
                <span className="text-gray-400 block font-medium">Годовая выручка:</span>
                <span className="text-base font-extrabold text-gray-900">
                  {latestFin ? `${Number(latestFin.annual_revenue).toLocaleString('ru-RU')} ₽` : '—'}
                </span>
              </div>
              <div>
                <span className="text-gray-400 block font-medium">Чистая прибыль:</span>
                <span
                  className={`text-base font-extrabold ${
                    latestFin && Number(latestFin.net_profit) < 0 ? 'text-rose-600' : 'text-emerald-700'
                  }`}
                >
                  {latestFin ? `${Number(latestFin.net_profit).toLocaleString('ru-RU')} ₽` : '—'}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <span className="text-gray-400 block font-medium">Общий долг:</span>
                  <span className="font-semibold text-gray-800">
                    {latestFin ? `${Number(latestFin.total_debt).toLocaleString('ru-RU')} ₽` : '—'}
                  </span>
                </div>
                <div>
                  <span className="text-gray-400 block font-medium">Платежи в месяц:</span>
                  <span className="font-semibold text-gray-800">
                    {latestFin ? `${Number(latestFin.monthly_credit_payments).toLocaleString('ru-RU')} ₽` : '—'}
                  </span>
                </div>
              </div>
              <div>
                <span className="text-gray-400 block font-medium">Возраст бизнеса:</span>
                <span className="font-semibold text-gray-800">{app.company?.business_age_years} г.</span>
              </div>
              <div>
                <span className="text-gray-400 block font-medium">Система налогообложения:</span>
                <span className="font-semibold text-gray-800">{app.company?.tax_system}</span>
              </div>
              <div>
                <span className="text-gray-400 block font-medium">ОКВЭД:</span>
                <span className="font-semibold text-gray-800">
                  {app.company?.okved} - {app.company?.okved_description}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Documents verification */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <FileText className="w-4 h-4 text-alfa-red" />
                Документы заемщика ({app.documents?.length || 0})
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-xs">
              {app.documents?.length === 0 ? (
                <div className="text-gray-400">Документы не прикреплены</div>
              ) : (
                app.documents?.map((doc) => (
                  <div
                    key={doc.id}
                    className="p-2.5 rounded-xl border border-gray-100 flex items-center justify-between"
                  >
                    <div>
                      <div className="font-bold text-gray-900">{doc.file_name}</div>
                      <div className="text-[11px] text-gray-400">{doc.doc_type_display}</div>
                    </div>
                    <span className="text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded text-[11px]">
                      {doc.is_verified ? 'Верифицирован' : 'К проверке'}
                    </span>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>

        {/* Col 2: External registries (FNS, BKI, Arbitration) */}
        <div className="lg:col-span-4 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-blue-600" />
                Внешние проверки (ФНС, БКИ, ЕГРЮЛ)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              {app.verification_results?.map((v) => (
                <div
                  key={v.id}
                  className={`p-3 rounded-xl border ${
                    v.status === 'PASSED'
                      ? 'border-emerald-200 bg-emerald-50/20'
                      : v.status === 'WARNING'
                      ? 'border-amber-200 bg-amber-50/20'
                      : 'border-rose-200 bg-rose-50/20'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-gray-900">{v.source_display}</span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        v.status === 'PASSED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : v.status === 'WARNING'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {v.status_display}
                    </span>
                  </div>
                  <div className="text-gray-700 leading-relaxed">{v.summary}</div>

                  {v.details && Object.keys(v.details).length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-100 grid grid-cols-2 gap-1 text-[11px] font-mono text-gray-500">
                      {Object.entries(v.details).map(([k, val]) => (
                        <div key={k} className="truncate">
                          {k}: <span className="font-semibold text-gray-800">{String(val)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Col 3: Scoring factors & Risk assessment */}
        <div className="lg:col-span-4 space-y-6">
          {scoring && (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-base">Скоринговый движок</CardTitle>
                  <p className="text-xs text-gray-400 mt-0.5">Детерминированная оценка риска</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-extrabold text-alfa-black">
                    {scoring.score} <span className="text-xs text-gray-400 font-normal">/ 100</span>
                  </div>
                  <div className="text-xs font-semibold text-emerald-700">{scoring.risk_level_display}</div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4 text-xs">
                {/* Stop Factors Alert if present */}
                {scoring.stop_factors && scoring.stop_factors.length > 0 && (
                  <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-800">
                    <div className="font-bold flex items-center gap-1.5 mb-1">
                      <AlertTriangle className="w-4 h-4 text-rose-600" />
                      Сработали стоп-факторы:
                    </div>
                    <ul className="list-disc list-inside space-y-0.5 text-[11px]">
                      {scoring.stop_factors.map((sf, i) => (
                        <li key={i}>{sf}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="text-gray-600 leading-relaxed bg-gray-50 p-3 rounded-xl">
                  {scoring.explanation}
                </div>

                {/* Factors List */}
                <div className="space-y-2">
                  <div className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                    Факторы скоринга:
                  </div>
                  {scoring.factors?.map((f, i) => (
                    <div
                      key={i}
                      className="p-2 rounded-lg border border-gray-100 flex items-center justify-between"
                    >
                      <div>
                        <span className="font-medium text-gray-800 block">{f.name}</span>
                        <span className="text-[10px] text-gray-400">{f.description}</span>
                      </div>
                      <span
                        className={`font-mono font-bold px-1.5 py-0.5 rounded text-[11px] ml-2 ${
                          f.type === 'POSITIVE'
                            ? 'bg-emerald-50 text-emerald-700'
                            : f.type === 'NEGATIVE'
                            ? 'bg-rose-50 text-rose-700'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {f.impact}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Underwriter Decision Modal */}
      <Modal
        isOpen={isDecisionModalOpen}
        onClose={() => setIsDecisionModalOpen(false)}
        title="Принятие андеррайтингового решения"
        description={`Заявка #${app.application_number} · ${app.company?.name}`}
        maxWidth="xl"
      >
        <div className="space-y-5">
          {/* Decision Type Tabs */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {[
              { id: 'APPROVED', label: 'Одобрить', color: 'emerald' },
              { id: 'COUNTER_OFFER', label: 'Встречные условия', color: 'amber' },
              { id: 'ADDITIONAL_INFO_REQUIRED', label: 'Запросить данные', color: 'blue' },
              { id: 'REJECTED', label: 'Отказать', color: 'rose' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setDecisionTab(tab.id as any)}
                className={`p-2.5 rounded-xl text-xs font-bold transition-all border ${
                  decisionTab === tab.id
                    ? 'bg-alfa-black text-white border-alfa-black shadow'
                    : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Form fields depending on selected decision */}
          {(decisionTab === 'APPROVED' || decisionTab === 'COUNTER_OFFER') && (
            <div className="space-y-3 bg-gray-50 p-4 rounded-xl border border-gray-200">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <Input
                  label="Одобренная сумма (руб)"
                  type="number"
                  value={approvedAmount}
                  onChange={(e) => setApprovedAmount(Number(e.target.value))}
                  required
                />
                <Input
                  label="Срок (месяцев)"
                  type="number"
                  value={approvedTerm}
                  onChange={(e) => setApprovedTerm(Number(e.target.value))}
                  required
                />
                <Input
                  label="Ставка (% годовых)"
                  type="number"
                  step="0.1"
                  value={approvedRate}
                  onChange={(e) => setApprovedRate(Number(e.target.value))}
                  required
                />
              </div>
            </div>
          )}

          {decisionTab === 'ADDITIONAL_INFO_REQUIRED' && (
            <div className="bg-blue-50/50 p-4 rounded-xl border border-blue-200 text-xs text-blue-900">
              <div className="font-bold mb-1">Запрос сведений у заемщика:</div>
              <div>Укажите, какие документы или пояснения необходимо предоставить предпринимателю.</div>
            </div>
          )}

          {decisionTab === 'REJECTED' && (
            <div>
              <label className="text-xs font-bold text-gray-700 uppercase tracking-wider block mb-1.5">
                Причины отказа (по одной на строке):
              </label>
              <textarea
                value={rejectionReasons}
                onChange={(e) => setRejectionReasons(e.target.value)}
                placeholder="Превышение комфортного уровня долговой нагрузки&#10;Наличие открытой налоговой задолженности"
                className="w-full p-3 bg-white border border-gray-200 rounded-xl text-xs focus:ring-alfa-red focus:border-alfa-red h-20"
              />
            </div>
          )}

          <div>
            <label className="text-xs font-bold text-gray-700 uppercase tracking-wider block mb-1.5">
              Обоснование решения (для клиента и внутреннего аудита):
            </label>
            <textarea
              value={decisionNotes}
              onChange={(e) => setDecisionNotes(e.target.value)}
              placeholder="Укажите комментарий, поясняющий расчет лимита или основания принятого решения..."
              className="w-full p-3 bg-white border border-gray-200 rounded-xl text-xs focus:ring-alfa-red focus:border-alfa-red h-24"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t border-gray-100">
            <Button variant="outline" size="md" onClick={() => setIsDecisionModalOpen(false)}>
              Отмена
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={handleApplyDecision}
              isLoading={actionLoading}
              className="font-bold"
            >
              Подтвердить решение
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
