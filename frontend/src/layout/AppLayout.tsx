import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';

export const AppLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-alfa-black font-sans">
      <Navbar />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        <Outlet />
      </main>
      <footer className="border-t border-gray-200 bg-white py-6 text-center text-xs text-gray-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="w-5 h-5 bg-alfa-red rounded-md text-white font-bold flex items-center justify-center text-xs">
              А
            </span>
            <span className="font-semibold text-gray-700">АО «Альфа-Банк»</span>
            <span>·</span>
            <span>Умный кредитный конвейер МСП 2026</span>
          </div>
          <div className="text-gray-400">
            Хакатон «Умный кредитный кабинет предпринимателя» · Демонстрационная версия
          </div>
        </div>
      </footer>
    </div>
  );
};
