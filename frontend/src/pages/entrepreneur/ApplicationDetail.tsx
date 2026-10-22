import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { applicationApi, decisionApi } from '../../api/client';
import { ApplicationDetail as ApplicationDetailType } from '../../types';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { StatusBadge } from '../../components/ui/Badge';
import {
  Building2,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ShieldCheck,
  FileText,
  TrendingUp,
  XCircle,
  HelpCircle,
  ArrowRight,
  Send,
  Sparkles,
} from 'lucide-react';

export const ApplicationDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [app, setApp] = useState<ApplicationDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [infoReply, setInfoReply] = useState('');

  const fetchApp = async () => {
    if (!id) return;
    try {
      const data = await applicationApi.get(Number(id));
      setApp(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApp();
  }, [id]);

  const handleClientRespond = async (accept: boolean) => {
    if (!id) return;
    setActionLoading(true);
    try {
      await decisionApi.clientRespond(Number(id), accept);
      await fetchApp();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleProvideInfo = async () => {
    if (!id || !infoReply.trim()) return;
    setActionLoading(true);
    try {
      await applicationApi.provideInfo(Number(id), infoReply);
      setInfoReply('');
      await fetchApp();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleSubmitDraft = async () => {
    if (!id) return;
    setActionLoading(true);
    try {
      await applicationApi.submit(Number(id));
      await fetchApp();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12 text-sm text-gray-500">Загрузка данных заявки...</div>;
  }

  if (!app) {
    return <div className="text-center py-12 text-sm text-gray-500">Заявка не найдена</div>;
  }

  const decision = app.decision;
  const scoring = app.scoring_result;

  // Pipeline Steps definition
  const pipelineSteps = [
    { key: 'SUBMITTED', label: 'Подача' },
    { key: 'VALIDATING', label: 'Валидация' },
    { key: 'ENRICHING', label: 'ФНС / БКИ' },
    { key: 'SCORING', label: 'Скоринг' },
    { key: 'DECISION', label: 'Решение' },
  ];

  const getStepIndex = (status: string) => {
    switch (status) {
      case 'DRAFT':
        return 0;
      case 'SUBMITTED':
        return 1;
      case 'VALIDATING':
        return 2;
      case 'ENRICHING':
        return 3;
      case 'SCORING':
        return 4;
      default:
        return 5;
    }
  };

  const currentStepIdx = getStepIndex(app.status);

  return (
    <div className="space-y-6">
      {/* Back link & Header */}
      <div>
        <Link to="/history" className="text-xs text-alfa-red hover:underline font-semibold flex items-center gap-1 mb-2">
          ← К списку заявок
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-alfa-black tracking-tight">
                Заявка #{app.application_number}
              </h1>
              <StatusBadge status={app.status} label={app.status_display} />
            </div>
            <p className="text-xs sm:text-sm text-gray-500 mt-1">
              {app.product?.name} · {app.company?.name} (ИНН {app.company?.inn})
            </p>
          </div>

          {app.status === 'DRAFT' && (
            <Button
              variant="primary"
              size="md"
              onClick={handleSubmitDraft}
              isLoading={actionLoading}
              leftIcon={<Sparkles className="w-4 h-4" />}
            >
              Отправить заявку на проверку
            </Button>
          )}
        </div>
      </div>

      {/* Visual Pipeline Stepper */}
      <Card className="p-5">
        <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">
          Кредитный конвейер заявки
        </div>
        <div className="flex items-center justify-between relative">
          <div className="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-gray-200 w-full z-0" />
          <div
            className="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-alfa-red transition-all duration-500 z-0"
            style={{ width: `${Math.min(100, (currentStepIdx / 4) * 100)}%` }}
          />

          {pipelineSteps.map((s, idx) => {
            const isDone = currentStepIdx > idx;
            const isCurrent = currentStepIdx === idx + 1;
            return (
              <div key={s.key} className="relative z-10 flex flex-col items-center">
                <div
                  className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                    isDone
                      ? 'bg-alfa-red text-white shadow-sm'
                      : isCurrent
                      ? 'bg-alfa-red text-white ring-4 ring-red-100 shadow'
                      : 'bg-white border-2 border-gray-300 text-gray-400'
                  }`}
                >
                  {isDone ? <CheckCircle2 className="w-4 h-4" /> : idx + 1}
                </div>
                <span className="text-[10px] sm:text-xs font-semibold text-gray-700 mt-1.5 hidden sm:inline">
                  {s.label}
                </span>
              </div>
            );
          })}
        </div>
      </Card>

      {/* DECISION & OFFER BANNER */}
      {app.status === 'OFFER_READY' && decision && (
        <div className="bg-white border-2 border-emerald-500 rounded-2xl p-6 shadow-md animate-in fade-in">
          <div className="flex items-center gap-2 text-emerald-700 font-extrabold text-sm uppercase tracking-wider mb-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            {decision.decision_type === 'COUNTER_OFFER'
              ? 'Встречное кредитное предложение банка'
              : 'Кредитное предложение сформировано'}
          </div>

          <p className="text-sm text-gray-700 leading-relaxed">{decision.rationale}</p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-emerald-50/50 p-4 rounded-xl my-4 text-xs">
            <div>
              <span className="text-gray-500 block">Одобренная сумма:</span>
              <span className="text-lg font-extrabold text-gray-900">
                {Number(decision.approved_amount).toLocaleString('ru-RU')} ₽
              </span>
            </div>
            <div>
              <span className="text-gray-500 block">Срок:</span>
              <span className="text-lg font-extrabold text-gray-900">{decision.approved_term_months} мес.</span>
            </div>
            <div>
              <span className="text-gray-500 block">Ставка:</span>
              <span className="text-lg font-extrabold text-emerald-700">{decision.approved_rate}%</span>
            </div>
            <div>
              <span className="text-gray-500 block">Ежемесячный платеж:</span>
              <span className="text-lg font-extrabold text-gray-900">
                {Number(decision.monthly_payment).toLocaleString('ru-RU')} ₽
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
            <Button
              variant="primary"
              size="lg"
              className="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-700 font-bold"
              onClick={() => handleClientRespond(true)}
              isLoading={actionLoading}
              leftIcon={<CheckCircle2 className="w-5 h-5" />}
            >
              Принять предложение и получить финансирование
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="w-full sm:w-auto text-gray-600"
              onClick={() => handleClientRespond(false)}
              disabled={actionLoading}
            >
              Отклонить предложение
            </Button>
          </div>
        </div>
      )}

      {/* COMPLETED SUCCESS BANNER */}
      {app.status === 'COMPLETED' && (
        <div className="bg-emerald-600 text-white rounded-2xl p-6 shadow-md flex items-center gap-4">
          <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center flex-shrink-0">
            <CheckCircle2 className="w-7 h-7 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-bold">Кредитный договор успешно оформлен!</h3>
            <p className="text-xs text-white/90 mt-1">
              Денежные средства по заявке #{app.application_number} в размере{' '}
              {Number(decision?.approved_amount || app.requested_amount).toLocaleString('ru-RU')} ₽ зачислены на расчетный счет компании.
            </p>
          </div>
        </div>
      )}

      {/* ADDITIONAL INFO REQUEST BANNER */}
      {app.status === 'ADDITIONAL_INFO_REQUIRED' && (
        <Card className="border-amber-400 bg-amber-50/40 p-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-base font-bold text-amber-900">
                Банку требуются дополнительные сведения для продолжения рассмотрения
              </h3>
              <p className="text-xs text-amber-800 mt-1 leading-relaxed">
                {decision?.rationale || 'Пожалуйста, уточните детали деятельности или прикрепите подтверждающие документы.'}
              </p>

              <div className="mt-4 space-y-3">
                <textarea
                  value={infoReply}
                  onChange={(e) => setInfoReply(e.target.value)}
                  placeholder="Введите ответ или пояснения для кредитного эксперта..."
                  className="w-full p-3 bg-white border border-amber-300 rounded-xl text-xs focus:ring-amber-400 focus:border-amber-500 h-24"
                />
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleProvideInfo}
                  isLoading={actionLoading}
                  leftIcon={<Send className="w-3.5 h-3.5" />}
                  className="bg-amber-600 hover:bg-amber-700"
                >
                  Отправить пояснения в банк
                </Button>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* REJECTED BANNER */}
      {app.status === 'REJECTED' && (
        <div className="bg-rose-50 border border-rose-200 rounded-2xl p-6 text-rose-900">
          <div className="flex items-start gap-3">
            <XCircle className="w-6 h-6 text-rose-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-base font-bold text-rose-950">По заявке принято отрицательное решение</h3>
              <p className="text-xs text-rose-800 mt-1 leading-relaxed">
                {decision?.rationale || 'Решение принято на основе автоматической скоринговой модели.'}
              </p>

              {decision?.rejection_reasons && decision.rejection_reasons.length > 0 && (
                <div className="mt-3">
                  <div className="text-xs font-bold text-rose-950 mb-1">Причины решения:</div>
                  <ul className="list-disc list-inside text-xs text-rose-800 space-y-0.5">
                    {decision.rejection_reasons.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: Parameters & Scoring */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Application Parameters & Scoring Results */}
        <div className="lg:col-span-8 space-y-6">
          {/* Scoring Engine Breakdown */}
          {scoring && (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-base">Оценка риска и прозрачный скоринг</CardTitle>
                  <p className="text-xs text-gray-500 mt-0.5">
                    Правила расчета баллов (Rule-Based Engine)
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-extrabold text-alfa-black">
                    {scoring.score} <span className="text-xs text-gray-400 font-normal">/ 100</span>
                  </div>
                  <div className="text-xs font-semibold text-emerald-700">{scoring.risk_level_display}</div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-xs text-gray-700 bg-gray-50 p-3 rounded-xl leading-relaxed">
                  {scoring.explanation}
                </p>

                {/* Factors List */}
                <div>
                  <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
                    Влияющие факторы оценки:
                  </div>
                  <div className="space-y-2">
                    {scoring.factors?.map((f, i) => (
                      <div
                        key={i}
                        className="p-2.5 rounded-xl border border-gray-100 flex items-center justify-between text-xs"
                      >
                        <div>
                          <span className="font-semibold text-gray-800 block">{f.name}</span>
                          <span className="text-gray-500 text-[11px]">{f.description}</span>
                        </div>
                        <span
                          className={`font-mono font-bold px-2 py-0.5 rounded text-xs ml-3 ${
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
                </div>
              </CardContent>
            </Card>
          )}

          {/* Verification Results Cards */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-alfa-red" />
                Результаты проверок государственных баз и реестров
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {app.verification_results?.map((v) => (
                <div
                  key={v.id}
                  className={`p-3.5 rounded-xl border text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2 ${
                    v.status === 'PASSED'
                      ? 'border-emerald-200 bg-emerald-50/30'
                      : v.status === 'WARNING'
                      ? 'border-amber-200 bg-amber-50/30'
                      : 'border-rose-200 bg-rose-50/30'
                  }`}
                >
                  <div>
                    <div className="font-bold text-gray-900">{v.source_display}</div>
                    <div className="text-gray-600 mt-0.5">{v.summary}</div>
                  </div>
                  <span
                    className={`px-2.5 py-1 rounded-md text-xs font-semibold self-start sm:self-auto ${
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
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Right: Summary & Status History */}
        <div className="lg:col-span-4 space-y-6">
          {/* Summary Card */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Параметры заявки</CardTitle>
            </CardHeader>
            <CardContent className="pt-3 space-y-3 text-xs">
              <div>
                <span className="text-gray-400 block font-medium">Запрошено:</span>
                <span className="text-base font-extrabold text-alfa-black">
                  {Number(app.requested_amount).toLocaleString('ru-RU')} ₽
                </span>
              </div>
              <div>
                <span className="text-gray-400 block font-medium">Срок:</span>
                <span className="font-bold text-gray-800">{app.term_months} месяцев</span>
              </div>
              <div>
                <span className="text-gray-400 block font-medium">Цель:</span>
                <span className="text-gray-700">{app.purpose}</span>
              </div>
              <div>
                <span className="text-gray-400 block font-medium">Компания:</span>
                <span className="font-semibold text-gray-800">{app.company?.name}</span>
              </div>
              <div>
                <span className="text-gray-400 block font-medium">ИНН:</span>
                <span className="font-mono font-semibold text-gray-800">{app.company?.inn}</span>
              </div>
            </CardContent>
          </Card>

          {/* Status History Timeline */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Clock className="w-4 h-4 text-gray-500" />
                История изменений
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-2">
              <div className="space-y-3 border-l-2 border-gray-200 pl-3 ml-2 text-xs">
                {app.status_history?.map((h) => (
                  <div key={h.id} className="relative">
                    <div className="absolute -left-[19px] top-1 w-2.5 h-2.5 rounded-full bg-alfa-red" />
                    <div className="font-bold text-gray-900">{h.to_status}</div>
                    <div className="text-gray-500 text-[11px]">{h.reason}</div>
                    <div className="text-[10px] text-gray-400 mt-0.5">
                      {new Date(h.created_at).toLocaleString([], {
                        day: '2-digit',
                        month: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
