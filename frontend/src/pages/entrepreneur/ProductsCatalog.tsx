import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { productApi } from '../../api/client';
import { CreditProduct } from '../../types';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import {
  TrendingUp,
  Briefcase,
  Cpu,
  Check,
  Calculator,
  ArrowRight,
  ShieldAlert,
  Percent,
  Calendar,
} from 'lucide-react';

export const ProductsCatalog: React.FC = () => {
  const navigate = useNavigate();
  const [products, setProducts] = useState<CreditProduct[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<CreditProduct | null>(null);

  // Calculator state
  const [amount, setAmount] = useState<number>(3000000);
  const [termMonths, setTermMonths] = useState<number>(12);
  const [calcResult, setCalcResult] = useState<{
    monthly_payment: number;
    total_repayment: number;
    total_overpayment: number;
  } | null>(null);

  useEffect(() => {
    productApi.list().then((list) => {
      setProducts(list);
      if (list.length > 0) {
        setSelectedProduct(list[0]);
      }
    });
  }, []);

  useEffect(() => {
    if (selectedProduct) {
      // Keep amount in bounds of selected product
      const minA = Number(selectedProduct.min_amount);
      const maxA = Number(selectedProduct.max_amount);
      const boundedAmount = Math.max(minA, Math.min(maxA, amount));
      if (boundedAmount !== amount) setAmount(boundedAmount);

      const minT = selectedProduct.min_term_months;
      const maxT = selectedProduct.max_term_months;
      const boundedTerm = Math.max(minT, Math.min(maxT, termMonths));
      if (boundedTerm !== termMonths) setTermMonths(boundedTerm);

      // Calculate
      productApi.calculate(selectedProduct.id, boundedAmount, boundedTerm).then(setCalcResult).catch(() => {});
    }
  }, [selectedProduct, amount, termMonths]);

  const getIcon = (icon: string) => {
    switch (icon) {
      case 'TrendingUp':
        return <TrendingUp className="w-5 h-5 text-alfa-red" />;
      case 'Briefcase':
        return <Briefcase className="w-5 h-5 text-alfa-red" />;
      case 'Cpu':
        return <Cpu className="w-5 h-5 text-alfa-red" />;
      default:
        return <Briefcase className="w-5 h-5 text-alfa-red" />;
    }
  };

  const handleApply = (product: CreditProduct) => {
    navigate(`/apply?productId=${product.id}&amount=${amount}&term=${termMonths}`);
  };

  return (
    <div className="space-y-8">
      {/* Title */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-alfa-black tracking-tight">
          Кредитные продукты для бизнеса
        </h1>
        <p className="text-xs sm:text-sm text-gray-500 mt-1">
          Выберите подходящую программу финансирования и рассчитайте предварительный график платежей.
        </p>
      </div>

      {/* Interactive Calculator Section */}
      <Card className="bg-gradient-to-br from-white via-white to-red-50/40 border-gray-200 shadow-sm overflow-hidden">
        <CardHeader className="bg-white/80 border-b border-gray-100 flex flex-row items-center gap-2">
          <Calculator className="w-5 h-5 text-alfa-red" />
          <CardTitle className="text-base sm:text-lg">Интерактивный кредитный калькулятор</CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Sliders */}
            <div className="lg:col-span-7 space-y-6">
              {/* Product selector buttons */}
              <div>
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-2">
                  Выберите программу:
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  {products.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => setSelectedProduct(p)}
                      className={`p-3 rounded-xl text-left border transition-all text-xs ${
                        selectedProduct?.id === p.id
                          ? 'border-alfa-red bg-red-50 text-alfa-black font-bold shadow-sm'
                          : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                      }`}
                    >
                      <div className="truncate">{p.name}</div>
                      <div className="text-[11px] text-gray-400 mt-0.5">от {p.base_rate}%</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Amount Slider */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Сумма финансирования:
                  </span>
                  <span className="text-lg font-extrabold text-alfa-black">
                    {amount.toLocaleString('ru-RU')} ₽
                  </span>
                </div>
                <input
                  type="range"
                  min={selectedProduct ? Number(selectedProduct.min_amount) : 300000}
                  max={selectedProduct ? Number(selectedProduct.max_amount) : 15000000}
                  step={100000}
                  value={amount}
                  onChange={(e) => setAmount(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-alfa-red"
                />
                <div className="flex justify-between text-[11px] text-gray-400 mt-1 font-mono">
                  <span>
                    {selectedProduct ? Number(selectedProduct.min_amount).toLocaleString('ru-RU') : '300 000'} ₽
                  </span>
                  <span>
                    {selectedProduct ? Number(selectedProduct.max_amount).toLocaleString('ru-RU') : '15 000 000'} ₽
                  </span>
                </div>
              </div>

              {/* Term Slider */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Срок кредита:
                  </span>
                  <span className="text-lg font-extrabold text-alfa-black">{termMonths} мес.</span>
                </div>
                <input
                  type="range"
                  min={selectedProduct ? selectedProduct.min_term_months : 3}
                  max={selectedProduct ? selectedProduct.max_term_months : 36}
                  step={1}
                  value={termMonths}
                  onChange={(e) => setTermMonths(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-alfa-red"
                />
                <div className="flex justify-between text-[11px] text-gray-400 mt-1 font-mono">
                  <span>{selectedProduct ? selectedProduct.min_term_months : 3} мес.</span>
                  <span>{selectedProduct ? selectedProduct.max_term_months : 36} мес.</span>
                </div>
              </div>
            </div>

            {/* Calculations Card */}
            <div className="lg:col-span-5 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
              <div>
                <div className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                  Ежемесячный платеж (аннуитет)
                </div>
                <div className="text-3xl font-extrabold text-alfa-red mt-1">
                  {calcResult
                    ? `${Number(calcResult.monthly_payment).toLocaleString('ru-RU')} ₽`
                    : 'Расчет...'}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Базовая ставка: <span className="font-bold text-gray-800">{selectedProduct?.base_rate}% годовых</span>
                </div>

                <div className="border-t border-gray-100 my-4 pt-4 space-y-2 text-xs">
                  <div className="flex justify-between text-gray-600">
                    <span>Сумма кредита:</span>
                    <span className="font-semibold text-gray-900">{amount.toLocaleString('ru-RU')} ₽</span>
                  </div>
                  <div className="flex justify-between text-gray-600">
                    <span>Переплата по процентам:</span>
                    <span className="font-semibold text-gray-900">
                      {calcResult ? `${Number(calcResult.total_overpayment).toLocaleString('ru-RU')} ₽` : '—'}
                    </span>
                  </div>
                  <div className="flex justify-between text-gray-600">
                    <span>Общая выплата за весь срок:</span>
                    <span className="font-semibold text-gray-900">
                      {calcResult ? `${Number(calcResult.total_repayment).toLocaleString('ru-RU')} ₽` : '—'}
                    </span>
                  </div>
                </div>
              </div>

              <Button
                variant="primary"
                size="lg"
                className="w-full mt-4 font-bold"
                onClick={() => selectedProduct && handleApply(selectedProduct)}
                rightIcon={<ArrowRight className="w-4 h-4" />}
              >
                Оформить заявку
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Catalog Cards */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 tracking-tight mb-4">
          Линейка кредитных продуктов Альфа-Банка
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {products.map((product) => (
            <Card
              key={product.id}
              className={`flex flex-col justify-between transition-all ${
                selectedProduct?.id === product.id ? 'ring-2 ring-alfa-red border-transparent shadow-md' : ''
              }`}
            >
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center">
                    {getIcon(product.icon)}
                  </div>
                  {product.badge_text && (
                    <Badge variant="alfa">{product.badge_text}</Badge>
                  )}
                </div>
                <CardTitle className="text-lg">{product.name}</CardTitle>
                <p className="text-xs text-gray-500 mt-1 leading-relaxed">{product.description}</p>
              </CardHeader>

              <CardContent className="pt-0 space-y-3 text-xs flex-1">
                <div className="bg-gray-50 p-3 rounded-xl space-y-1.5 font-mono">
                  <div className="flex justify-between">
                    <span className="text-gray-500 font-sans">Ставка:</span>
                    <span className="font-bold text-alfa-black">от {product.base_rate}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 font-sans">Сумма:</span>
                    <span className="font-bold text-gray-800">
                      до {Number(product.max_amount).toLocaleString('ru-RU')} ₽
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 font-sans">Срок:</span>
                    <span className="font-bold text-gray-800">до {product.max_term_months} мес.</span>
                  </div>
                </div>

                <div className="space-y-1 pt-1">
                  <div className="text-gray-400 font-medium">Требуемые документы:</div>
                  {product.required_documents?.map((doc, idx) => (
                    <div key={idx} className="flex items-center gap-1.5 text-gray-700">
                      <Check className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                      <span className="truncate">{doc}</span>
                    </div>
                  ))}
                </div>
              </CardContent>

              <CardFooter className="pt-4">
                <Button
                  variant={selectedProduct?.id === product.id ? 'primary' : 'outline'}
                  size="md"
                  className="w-full font-semibold"
                  onClick={() => handleApply(product)}
                >
                  Подать заявку
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};
