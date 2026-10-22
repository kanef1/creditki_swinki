import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Card, CardContent } from '../../components/ui/Card';
import { ShieldCheck, UserCheck, ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';

export const Login: React.FC = () => {
  const { login, quickLogin } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState('entrepreneur_a');
  const [password, setPassword] = useState('alfa2026pass');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      await login(username, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Неверный логин или пароль');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuick = async (user: string, route = '/') => {
    setIsLoading(true);
    try {
      await quickLogin(user);
      navigate(route);
    } catch (err) {
      setError('Ошибка быстрого входа.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-14 h-14 bg-alfa-red rounded-2xl text-white font-extrabold text-2xl mb-3 shadow-md">
          А
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-alfa-black tracking-tight">
          Умный кредитный кабинет предпринимателя
        </h1>
        <p className="text-gray-500 text-sm mt-2 max-w-lg mx-auto">
          Цифровой конвейер Альфа-Банка для малого и микробизнеса. Мгновенная верификация, скоринг и прозрачные решения.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Standard Login Form */}
        <div className="md:col-span-5">
          <Card className="h-full">
            <CardContent className="p-6">
              <h2 className="text-base font-bold text-gray-900 mb-4">Вход в личный кабинет</h2>

              {error && (
                <div className="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                  label="Логин"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Введите имя пользователя"
                  required
                />
                <Input
                  label="Пароль"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
                <Button type="submit" variant="primary" className="w-full" isLoading={isLoading}>
                  Войти
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Demo Fast Login Switcher Cards */}
        <div className="md:col-span-7">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-400">
              Быстрый вход для проверки сценариев (Жюри)
            </span>
          </div>

          <div className="space-y-2.5">
            {/* Scenario A */}
            <div
              onClick={() => handleQuick('entrepreneur_a', '/')}
              className="p-3.5 bg-white rounded-xl border border-gray-200 hover:border-alfa-red hover:shadow-sm cursor-pointer transition-all flex items-center justify-between group"
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-sm">
                  A
                </div>
                <div>
                  <div className="text-sm font-bold text-gray-900 group-hover:text-alfa-red transition-colors">
                    Сценарий A: Автоодобрение
                  </div>
                  <div className="text-xs text-gray-500">
                    ООО «ТехноПрогресс» · Выручка 48 млн ₽ · Рейтинг 100/100
                  </div>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-alfa-red group-hover:translate-x-1 transition-all" />
            </div>

            {/* Scenario B */}
            <div
              onClick={() => handleQuick('entrepreneur_b', '/')}
              className="p-3.5 bg-white rounded-xl border border-gray-200 hover:border-alfa-red hover:shadow-sm cursor-pointer transition-all flex items-center justify-between group"
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-bold text-sm">
                  B
                </div>
                <div>
                  <div className="text-sm font-bold text-gray-900 group-hover:text-alfa-red transition-colors">
                    Сценарий B: Встречное предложение
                  </div>
                  <div className="text-xs text-gray-500">
                    ИП Иванов А.С. · Запрос превышает лимит долговой нагрузки
                  </div>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-alfa-red group-hover:translate-x-1 transition-all" />
            </div>

            {/* Scenario C */}
            <div
              onClick={() => handleQuick('entrepreneur_c', '/')}
              className="p-3.5 bg-white rounded-xl border border-gray-200 hover:border-alfa-red hover:shadow-sm cursor-pointer transition-all flex items-center justify-between group"
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-sm">
                  C
                </div>
                <div>
                  <div className="text-sm font-bold text-gray-900 group-hover:text-alfa-red transition-colors">
                    Сценарий C: Ручное рассмотрение
                  </div>
                  <div className="text-xs text-gray-500">
                    ООО «Вектор Плюс» · Молодой бизнес + историческая просрочка БКИ
                  </div>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-alfa-red group-hover:translate-x-1 transition-all" />
            </div>

            {/* Scenario D */}
            <div
              onClick={() => handleQuick('entrepreneur_d', '/')}
              className="p-3.5 bg-white rounded-xl border border-gray-200 hover:border-alfa-red hover:shadow-sm cursor-pointer transition-all flex items-center justify-between group"
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-rose-100 text-rose-700 flex items-center justify-center font-bold text-sm">
                  D
                </div>
                <div>
                  <div className="text-sm font-bold text-gray-900 group-hover:text-alfa-red transition-colors">
                    Сценарий D: Отказ со стоп-факторами
                  </div>
                  <div className="text-xs text-gray-500">
                    ООО «СтройНеликвид» · Налоговый долг ФНС + просрочка БКИ 90+
                  </div>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-alfa-red group-hover:translate-x-1 transition-all" />
            </div>

            {/* Officer */}
            <div
              onClick={() => handleQuick('officer_alfa', '/bank')}
              className="p-3.5 bg-gray-900 text-white rounded-xl border border-gray-800 hover:border-alfa-red hover:shadow-md cursor-pointer transition-all flex items-center justify-between group"
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-red-600 text-white flex items-center justify-center font-bold text-sm">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-sm font-bold text-white group-hover:text-alfa-red transition-colors">
                    Кабинет сотрудника банка (Андеррайтера)
                  </div>
                  <div className="text-xs text-gray-400">
                    Кузнецова Елена · Очередь заявок, оценка рисков и ручные решения
                  </div>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-alfa-red group-hover:translate-x-1 transition-all" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
