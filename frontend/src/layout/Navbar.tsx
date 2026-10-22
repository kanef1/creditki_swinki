import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Briefcase,
  FileText,
  Clock,
  ShieldCheck,
  Bell,
  LogOut,
  Building2,
  Sparkles,
  ChevronDown,
  RefreshCw,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { notificationApi, demoApi } from '../api/client';
import { InAppNotification } from '../types';

export const Navbar: React.FC = () => {
  const { user, logout, quickLogin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const [notifications, setNotifications] = useState<InAppNotification[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [isResetting, setIsResetting] = useState(false);

  useEffect(() => {
    if (user) {
      notificationApi.list().then(setNotifications).catch(() => {});
    }
  }, [user, location.pathname]);

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const handleMarkAllRead = async () => {
    await notificationApi.markAllRead();
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };

  const handleResetDemoData = async () => {
    if (confirm('Сбросить все данные к исходным демонстрационным сценариям?')) {
      setIsResetting(true);
      try {
        await demoApi.reset();
        window.location.reload();
      } finally {
        setIsResetting(false);
      }
    }
  };

  return (
    <>
      {/* Top Demo Bar for Hackathon Jury */}
      <div className="bg-alfa-black text-white text-xs px-4 py-2 border-b border-gray-800">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 rounded-full bg-alfa-red animate-pulse"></span>
            <span className="font-semibold text-gray-300">Хакатон Альфа-Банка | Быстрое переключение сценариев:</span>
          </div>

          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
            <button
              onClick={() => quickLogin('entrepreneur_a').then(() => navigate('/'))}
              className={`px-2.5 py-1 rounded text-xs transition-colors ${
                user?.username === 'entrepreneur_a'
                  ? 'bg-alfa-red text-white font-bold'
                  : 'bg-gray-800 hover:bg-gray-700 text-gray-200'
              }`}
              title="ООО ТехноПрогресс: выручка 48М, авто-одобрение"
            >
              Сценарий A: Автоодобрение
            </button>
            <button
              onClick={() => quickLogin('entrepreneur_b').then(() => navigate('/'))}
              className={`px-2.5 py-1 rounded text-xs transition-colors ${
                user?.username === 'entrepreneur_b'
                  ? 'bg-alfa-red text-white font-bold'
                  : 'bg-gray-800 hover:bg-gray-700 text-gray-200'
              }`}
              title="ИП Иванов: запрос 6М, встречное на 3.6М"
            >
              Сценарий B: Встречное
            </button>
            <button
              onClick={() => quickLogin('entrepreneur_c').then(() => navigate('/'))}
              className={`px-2.5 py-1 rounded text-xs transition-colors ${
                user?.username === 'entrepreneur_c'
                  ? 'bg-alfa-red text-white font-bold'
                  : 'bg-gray-800 hover:bg-gray-700 text-gray-200'
              }`}
              title="ООО Вектор Плюс: на ручном рассмотрении"
            >
              Сценарий C: Андеррайтинг
            </button>
            <button
              onClick={() => quickLogin('entrepreneur_d').then(() => navigate('/'))}
              className={`px-2.5 py-1 rounded text-xs transition-colors ${
                user?.username === 'entrepreneur_d'
                  ? 'bg-alfa-red text-white font-bold'
                  : 'bg-gray-800 hover:bg-gray-700 text-gray-200'
              }`}
              title="ООО СтройНеликвид: долги ФНС, стоп-факторы"
            >
              Сценарий D: Отказ
            </button>
            <div className="h-4 w-px bg-gray-700 mx-1"></div>
            <button
              onClick={() => quickLogin('officer_alfa').then(() => navigate('/bank'))}
              className={`px-2.5 py-1 rounded text-xs transition-colors ${
                user?.role === 'BANK_OFFICER'
                  ? 'bg-red-600 text-white font-bold'
                  : 'bg-red-950 text-red-200 hover:bg-red-900'
              }`}
              title="Рабочее место кредитного офицера"
            >
              Кабинет банка
            </button>
            <button
              onClick={handleResetDemoData}
              disabled={isResetting}
              className="px-2 py-1 bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white rounded text-xs flex items-center gap-1"
              title="Восстановить демонстрационные данные"
            >
              <RefreshCw className={`w-3 h-3 ${isResetting ? 'animate-spin' : ''}`} />
              Сброс
            </button>
          </div>
        </div>
      </div>

      {/* Main Navbar */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-6">
              <Link to="/" className="flex items-center gap-3 group">
                <div className="w-9 h-9 bg-alfa-red rounded-xl flex items-center justify-center text-white font-extrabold text-xl shadow-sm group-hover:bg-alfa-red-hover transition-colors">
                  А
                </div>
                <div>
                  <div className="text-base font-extrabold tracking-tight text-alfa-black flex items-center gap-1.5">
                    Альфа-Банк
                    <span className="text-xs px-2 py-0.5 bg-red-100 text-alfa-red font-semibold rounded-md">
                      Кредиты МСП
                    </span>
                  </div>
                  <div className="text-[11px] text-gray-400 font-medium leading-none">
                    Умный кредитный кабинет
                  </div>
                </div>
              </Link>

              {/* Navigation Links */}
              {user && (
                <nav className="hidden md:flex items-center gap-1 ml-4">
                  {user.role === 'ENTREPRENEUR' ? (
                    <>
                      <Link
                        to="/"
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          location.pathname === '/'
                            ? 'text-alfa-red bg-red-50 font-semibold'
                            : 'text-gray-600 hover:text-alfa-black hover:bg-gray-50'
                        }`}
                      >
                        Главная
                      </Link>
                      <Link
                        to="/products"
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          location.pathname === '/products'
                            ? 'text-alfa-red bg-red-50 font-semibold'
                            : 'text-gray-600 hover:text-alfa-black hover:bg-gray-50'
                        }`}
                      >
                        Кредитные продукты
                      </Link>
                      <Link
                        to="/history"
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          location.pathname === '/history'
                            ? 'text-alfa-red bg-red-50 font-semibold'
                            : 'text-gray-600 hover:text-alfa-black hover:bg-gray-50'
                        }`}
                      >
                        Мои заявки
                      </Link>
                    </>
                  ) : (
                    <>
                      <Link
                        to="/bank"
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          location.pathname === '/bank'
                            ? 'text-alfa-red bg-red-50 font-semibold'
                            : 'text-gray-600 hover:text-alfa-black hover:bg-gray-50'
                        }`}
                      >
                        Очередь андеррайтинга
                      </Link>
                    </>
                  )}
                </nav>
              )}
            </div>

            {/* Right Side: Quick Action + Notification + User */}
            <div className="flex items-center gap-3">
              {user?.role === 'ENTREPRENEUR' && (
                <Link
                  to="/apply"
                  className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-2 bg-alfa-red hover:bg-alfa-red-hover text-white text-xs sm:text-sm font-semibold rounded-xl shadow-sm transition-all"
                >
                  <Sparkles className="w-4 h-4" />
                  Подать заявку
                </Link>
              )}

              {/* Notifications */}
              {user && (
                <div className="relative">
                  <button
                    onClick={() => setShowNotifications(!showNotifications)}
                    className="p-2 text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded-xl transition-colors relative"
                    aria-label="Уведомления"
                  >
                    <Bell className="w-5 h-5" />
                    {unreadCount > 0 && (
                      <span className="absolute top-1.5 right-1.5 w-4 h-4 bg-alfa-red text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                        {unreadCount}
                      </span>
                    )}
                  </button>

                  {/* Dropdown */}
                  {showNotifications && (
                    <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-2xl shadow-xl border border-gray-100 p-4 z-50 animate-in fade-in zoom-in-95">
                      <div className="flex items-center justify-between pb-3 border-b border-gray-100">
                        <span className="font-bold text-sm text-alfa-black">Уведомления</span>
                        {unreadCount > 0 && (
                          <button
                            onClick={handleMarkAllRead}
                            className="text-xs text-alfa-red hover:underline font-medium"
                          >
                            Прочитать все
                          </button>
                        )}
                      </div>

                      <div className="max-h-72 overflow-y-auto divide-y divide-gray-50 mt-2">
                        {notifications.length === 0 ? (
                          <div className="text-center py-6 text-xs text-gray-400">
                            Нет новых уведомлений
                          </div>
                        ) : (
                          notifications.map((n) => (
                            <div
                              key={n.id}
                              className={`py-2.5 px-2 rounded-lg text-xs ${
                                !n.is_read ? 'bg-red-50/50 font-medium' : ''
                              }`}
                            >
                              <div className="font-semibold text-gray-900">{n.title}</div>
                              <div className="text-gray-600 mt-0.5">{n.message}</div>
                              <div className="text-[10px] text-gray-400 mt-1">
                                {new Date(n.created_at).toLocaleTimeString([], {
                                  hour: '2-digit',
                                  minute: '2-digit',
                                })}
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* User Profile / Logout */}
              {user ? (
                <div className="flex items-center gap-2 pl-2 border-l border-gray-200">
                  <div className="hidden sm:block text-right">
                    <div className="text-xs font-bold text-gray-900 leading-tight">
                      {user.first_name} {user.last_name || user.username}
                    </div>
                    <div className="text-[11px] text-gray-400">
                      {user.role === 'BANK_OFFICER' ? 'Андеррайтер банка' : user.position || 'Заемщик'}
                    </div>
                  </div>

                  <button
                    onClick={() => logout().then(() => navigate('/login'))}
                    className="p-2 text-gray-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors"
                    title="Выйти из кабинета"
                  >
                    <LogOut className="w-5 h-5" />
                  </button>
                </div>
              ) : (
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm font-semibold text-alfa-black hover:text-alfa-red transition-colors"
                >
                  Войти
                </Link>
              )}
            </div>
          </div>
        </div>
      </header>
    </>
  );
};
