import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { productApi, companyApi, applicationApi, documentApi } from '../../api/client';
import { CreditProduct, Company } from '../../types';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import {
  Check,
  ChevronRight,
  ChevronLeft,
  Building2,
  FileCheck2,
  Upload,
  AlertCircle,
  Sparkles,
  Search,
  CheckCircle,
} from 'lucide-react';

export const ApplicationWizard: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user } = useAuth();

  const [step, setStep] = useState<number>(1);
  const [products, setProducts] = useState<CreditProduct[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [productId, setProductId] = useState<number>(0);
  const [amount, setAmount] = useState<number>(3000000);
  const [termMonths, setTermMonths] = useState<number>(12);
  const [purpose, setPurpose] = useState<string>('Пополнение оборотных средств');
  const [comments, setComments] = useState<string>('');

  // Company State
  const [companyId, setCompanyId] = useState<number>(0);
  const [innInput, setInnInput] = useState<string>('7701234567');
  const [companyName, setCompanyName] = useState<string>('');
  const [ceoName, setCeoName] = useState<string>('');
  const [address, setAddress] = useState<string>('');
  const [taxSystem, setTaxSystem] = useState<string>('УСН (Доходы минус расходы)');
  const [isLookingUpInn, setIsLookingUpInn] = useState<boolean>(false);

  // Financials State
  const [revenue, setRevenue] = useState<number>(48000000);
  const [profit, setProfit] = useState<number>(7200000);
  const [debt, setDebt] = useState<number>(1500000);
  const [monthlyPmt, setMonthlyPmt] = useState<number>(85000);

  // Uploaded documents state (simulated or real)
  const [uploadedFiles, setUploadedFiles] = useState<{ name: string; type: string }[]>([
    { name: 'Бухгалтерский_баланс_2025.pdf', type: 'FINANCIAL_STATEMENT' },
    { name: 'Выписка_расчетный_счет_12мес.pdf', type: 'BANK_STATEMENT' },
  ]);

  useEffect(() => {
    const initData = async () => {
      try {
        const [prodList, compList] = await Promise.all([
          productApi.list(),
          companyApi.list(),
        ]);
        setProducts(prodList);
        setCompanies(compList);

        // Preselect from URL query if present
        const qProdId = Number(searchParams.get('productId'));
        const qAmount = Number(searchParams.get('amount'));
        const qTerm = Number(searchParams.get('term'));

        if (qProdId) setProductId(qProdId);
        else if (prodList.length > 0) setProductId(prodList[0].id);

        if (qAmount) setAmount(qAmount);
        if (qTerm) setTermMonths(qTerm);

        if (compList.length > 0) {
          const comp = compList[0];
          setCompanyId(comp.id);
          setInnInput(comp.inn);
          setCompanyName(comp.name);
          setCeoName(comp.ceo_name);
          setAddress(comp.legal_address);
          setTaxSystem(comp.tax_system);

          const fin = comp.financial_reports?.[0];
          if (fin) {
            setRevenue(Number(fin.annual_revenue));
            setProfit(Number(fin.net_profit));
            setDebt(Number(fin.total_debt));
            setMonthlyPmt(Number(fin.monthly_credit_payments));
          }
        }
      } catch (err) {
        console.error('Wizard init error', err);
      }
    };
    initData();
  }, [searchParams]);

  const selectedProduct = products.find((p) => p.id === productId);

  const handleLookupInn = async () => {
    if (!innInput || innInput.length < 10) {
      setError('Введите корректный ИНН (10 или 12 цифр)');
      return;
    }
    setIsLookingUpInn(true);
    setError(null);
    try {
      const data = await companyApi.lookupByInn(innInput);
      if (data) {
        setCompanyName(data.name || '');
        setCeoName(data.ceo_name || '');
        setAddress(data.legal_address || '');
        setTaxSystem(data.tax_system || 'УСН (Доходы)');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Организация с таким ИНН не найдена.');
    } finally {
      setIsLookingUpInn(false);
    }
  };

  const handleSaveOrSubmit = async (autoSubmit: boolean) => {
    setError(null);
    setIsSubmitting(true);

    try {
      // 1. Ensure company exists in DB
      let finalCompanyId = companyId;
      if (!finalCompanyId) {
        const newComp = await companyApi.create({
          inn: innInput,
          name: companyName || `ООО "Компания ${innInput}"`,
          ceo_name: ceoName || 'Иванов Алексей',
          legal_address: address || 'г. Москва',
          tax_system: taxSystem,
          registration_date: '2022-01-15',
          okved: '62.01',
        });
        finalCompanyId = newComp.id;
      }

      // 2. Update financials
      await companyApi.updateFinancials(finalCompanyId, {
        year: 2025,
        annual_revenue: revenue,
        net_profit: profit,
        total_debt: debt,
        monthly_credit_payments: monthlyPmt,
      });

      // 3. Create application
      const app = await applicationApi.create({
        company: finalCompanyId,
        product: productId,
        requested_amount: amount,
        term_months: termMonths,
        purpose,
        additional_comments: comments,
        auto_submit: autoSubmit,
      });

      // Navigate to application details
      navigate(`/applications/${app.id}`);
    } catch (err: any) {
      setError(err.response?.data?.requested_amount || err.message || 'Ошибка сохранения заявки.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Wizard Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-alfa-black tracking-tight">
          Оформление кредитной заявки
        </h1>
        <p className="text-xs sm:text-sm text-gray-500 mt-1">
          Пройдите 4 простых шага для подачи заявки и моментального скоринга.
        </p>
      </div>

      {/* Stepper Bar */}
      <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm">
        <div className="grid grid-cols-4 gap-2 text-center text-xs">
          {[
            { stepNum: 1, title: 'Условия кредита' },
            { stepNum: 2, title: 'Организация' },
            { stepNum: 3, title: 'Финансы и документы' },
            { stepNum: 4, title: 'Подтверждение' },
          ].map((item) => (
            <div
              key={item.stepNum}
              className={`flex flex-col items-center gap-1.5 cursor-pointer ${
                step === item.stepNum
                  ? 'text-alfa-red font-bold'
                  : step > item.stepNum
                  ? 'text-gray-900 font-medium'
                  : 'text-gray-400'
              }`}
              onClick={() => item.stepNum < step && setStep(item.stepNum)}
            >
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                  step === item.stepNum
                    ? 'bg-alfa-red text-white shadow'
                    : step > item.stepNum
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-gray-100 text-gray-400'
                }`}
              >
                {step > item.stepNum ? <Check className="w-4 h-4" /> : item.stepNum}
              </div>
              <span className="hidden sm:inline">{item.title}</span>
            </div>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* STEP 1: Product & Terms */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Шаг 1. Выбор кредитного продукта и условий</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <label className="text-xs font-bold text-gray-700 uppercase tracking-wider block mb-2">
                Кредитный продукт:
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {products.map((p) => (
                  <div
                    key={p.id}
                    onClick={() => setProductId(p.id)}
                    className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                      productId === p.id
                        ? 'border-alfa-red bg-red-50/50 shadow-sm'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-bold text-sm text-gray-900">{p.name}</div>
                    <div className="text-xs text-alfa-red font-semibold mt-1">от {p.base_rate}% годовых</div>
                    <div className="text-[11px] text-gray-400 mt-2">
                      Лимит до {Number(p.max_amount).toLocaleString('ru-RU')} ₽
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Запрашиваемая сумма (руб)"
                type="number"
                value={amount}
                onChange={(e) => setAmount(Number(e.target.value))}
                min={selectedProduct ? Number(selectedProduct.min_amount) : 300000}
                max={selectedProduct ? Number(selectedProduct.max_amount) : 15000000}
                step={50000}
                helperText={`Лимит продукта: от ${
                  selectedProduct ? Number(selectedProduct.min_amount).toLocaleString('ru-RU') : '0'
                } до ${
                  selectedProduct ? Number(selectedProduct.max_amount).toLocaleString('ru-RU') : '0'
                } ₽`}
                required
              />
              <Input
                label="Срок кредита (месяцев)"
                type="number"
                value={termMonths}
                onChange={(e) => setTermMonths(Number(e.target.value))}
                min={selectedProduct ? selectedProduct.min_term_months : 3}
                max={selectedProduct ? selectedProduct.max_term_months : 36}
                helperText={`Срок: от ${selectedProduct?.min_term_months || 3} до ${
                  selectedProduct?.max_term_months || 36
                } месяцев`}
                required
              />
            </div>

            <div>
              <label className="text-xs font-bold text-gray-700 uppercase tracking-wider block mb-1.5">
                Цель финансирования:
              </label>
              <select
                value={purpose}
                onChange={(e) => setPurpose(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-white border border-gray-200 rounded-xl text-sm focus:border-alfa-red focus:ring-red-100"
              >
                <option value="Пополнение оборотных средств">Пополнение оборотных средств</option>
                <option value="Закупка оборудования и модернизация">Закупка оборудования и модернизация</option>
                <option value="Расширение сети и новые проекты">Расширение сети и новые проекты</option>
                <option value="Кассовый разрыв и операционные расходы">
                  Кассовый разрыв и операционные расходы
                </option>
              </select>
            </div>
          </CardContent>
          <CardFooter className="flex justify-end">
            <Button
              variant="primary"
              size="md"
              onClick={() => setStep(2)}
              rightIcon={<ChevronRight className="w-4 h-4" />}
            >
              Далее к данным компании
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* STEP 2: Company & INN */}
      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle>Шаг 2. Данные организации и реквизиты</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col sm:flex-row items-end gap-2">
              <div className="flex-1 w-full">
                <Input
                  label="ИНН организации или ИП"
                  value={innInput}
                  onChange={(e) => setInnInput(e.target.value)}
                  placeholder="10 или 12 цифр"
                  helperText="Введите ИНН и нажмите 'Заполнить по ИНН' для автозаполнения из реестра"
                  required
                />
              </div>
              <Button
                type="button"
                variant="outline"
                size="md"
                onClick={handleLookupInn}
                isLoading={isLookingUpInn}
                leftIcon={<Search className="w-4 h-4" />}
              >
                Заполнить по ИНН
              </Button>
            </div>

            <Input
              label="Наименование компании / ФИО ИП"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="ООО / ИП ..."
              required
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="ФИО Руководителя"
                value={ceoName}
                onChange={(e) => setCeoName(e.target.value)}
                placeholder="Иванов Алексей Сергеевич"
                required
              />
              <Input
                label="Система налогообложения"
                value={taxSystem}
                onChange={(e) => setTaxSystem(e.target.value)}
                placeholder="УСН / ОСНО"
              />
            </div>

            <Input
              label="Юридический адрес"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="г. Москва, ул. ..."
            />
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button
              variant="outline"
              size="md"
              onClick={() => setStep(1)}
              leftIcon={<ChevronLeft className="w-4 h-4" />}
            >
              Назад
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={() => setStep(3)}
              rightIcon={<ChevronRight className="w-4 h-4" />}
            >
              Далее к финансовым показателям
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* STEP 3: Financials & Documents */}
      {step === 3 && (
        <Card>
          <CardHeader>
            <CardTitle>Шаг 3. Финансовые показатели и подтверждающие документы</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Годовая выручка (руб)"
                type="number"
                value={revenue}
                onChange={(e) => setRevenue(Number(e.target.value))}
                helperText="Общий объем поступлений за последний календарный год"
                required
              />
              <Input
                label="Чистая прибыль за год (руб)"
                type="number"
                value={profit}
                onChange={(e) => setProfit(Number(e.target.value))}
                helperText="Итоговый финансовый результат"
                required
              />
              <Input
                label="Текущие кредитные обязательства (руб)"
                type="number"
                value={debt}
                onChange={(e) => setDebt(Number(e.target.value))}
                helperText="Остаток задолженности по всем кредитам и лизингу"
              />
              <Input
                label="Ежемесячный платеж по кредитам (руб)"
                type="number"
                value={monthlyPmt}
                onChange={(e) => setMonthlyPmt(Number(e.target.value))}
                helperText="Суммарный ежемесячный взнос по текущим займам"
              />
            </div>

            {/* Document Upload Area */}
            <div>
              <label className="text-xs font-bold text-gray-700 uppercase tracking-wider block mb-2">
                Прикрепленные документы (Форма 1/2, выписка):
              </label>
              <div className="border-2 border-dashed border-gray-200 hover:border-alfa-red rounded-2xl p-6 text-center transition-colors bg-gray-50/50">
                <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <div className="text-xs font-bold text-gray-700">Перетащите файлы сюда или нажмите для выбора</div>
                <div className="text-[11px] text-gray-400 mt-1">Поддерживаются форматы PDF, PNG, JPG до 20 МБ</div>
              </div>

              {/* Uploaded documents list */}
              <div className="mt-3 space-y-2">
                {uploadedFiles.map((f, i) => (
                  <div
                    key={i}
                    className="p-3 bg-white rounded-xl border border-gray-200 flex items-center justify-between text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <FileCheck2 className="w-4 h-4 text-emerald-600" />
                      <span className="font-medium text-gray-800">{f.name}</span>
                    </div>
                    <span className="text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded">
                      Готов к проверке
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-gray-700 uppercase tracking-wider block mb-1.5">
                Дополнительные комментарии для андеррайтера (опционально):
              </label>
              <textarea
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                placeholder="Укажите особенности бизнеса, сезонность или детали контрактов..."
                className="w-full px-3.5 py-2.5 bg-white border border-gray-200 rounded-xl text-sm focus:border-alfa-red focus:ring-red-100 h-20"
              />
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button
              variant="outline"
              size="md"
              onClick={() => setStep(2)}
              leftIcon={<ChevronLeft className="w-4 h-4" />}
            >
              Назад
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={() => setStep(4)}
              rightIcon={<ChevronRight className="w-4 h-4" />}
            >
              Перейти к подтверждению
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* STEP 4: Review & Submit */}
      {step === 4 && (
        <Card>
          <CardHeader>
            <CardTitle>Шаг 4. Проверка условий и подача заявки</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-gray-400 block">Продукт:</span>
                  <span className="font-bold text-gray-900 text-sm">{selectedProduct?.name}</span>
                </div>
                <div>
                  <span className="text-gray-400 block">Организация:</span>
                  <span className="font-bold text-gray-900 text-sm">
                    {companyName} (ИНН {innInput})
                  </span>
                </div>
                <div>
                  <span className="text-gray-400 block">Запрашиваемая сумма:</span>
                  <span className="font-extrabold text-alfa-red text-base">
                    {amount.toLocaleString('ru-RU')} ₽
                  </span>
                </div>
                <div>
                  <span className="text-gray-400 block">Срок финансирования:</span>
                  <span className="font-bold text-gray-900 text-base">{termMonths} мес.</span>
                </div>
                <div>
                  <span className="text-gray-400 block">Годовая выручка:</span>
                  <span className="font-semibold text-gray-800">{revenue.toLocaleString('ru-RU')} ₽</span>
                </div>
                <div>
                  <span className="text-gray-400 block">Чистая прибыль:</span>
                  <span className="font-semibold text-gray-800">{profit.toLocaleString('ru-RU')} ₽</span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-emerald-50/60 border border-emerald-200 rounded-2xl text-xs text-emerald-900 flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <div className="font-bold">Согласие на автоматическую обработку</div>
                <div className="text-emerald-800 mt-0.5">
                  Нажимая кнопку «Отправить заявку в банк», вы даете согласие АО «Альфа-Банк» на получение кредитного отчета в БКИ и запрос регистрационных данных из ФНС России.
                </div>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col sm:flex-row items-center justify-between gap-3">
            <Button
              variant="outline"
              size="md"
              onClick={() => setStep(3)}
              leftIcon={<ChevronLeft className="w-4 h-4" />}
              disabled={isSubmitting}
            >
              Назад
            </Button>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Button
                variant="outline"
                size="md"
                onClick={() => handleSaveOrSubmit(false)}
                isLoading={isSubmitting}
                className="flex-1 sm:flex-none"
              >
                Сохранить черновик
              </Button>
              <Button
                variant="primary"
                size="md"
                onClick={() => handleSaveOrSubmit(true)}
                isLoading={isSubmitting}
                rightIcon={<Sparkles className="w-4 h-4" />}
                className="flex-1 sm:flex-none font-bold"
              >
                Отправить заявку в банк
              </Button>
            </div>
          </CardFooter>
        </Card>
      )}
    </div>
  );
};
