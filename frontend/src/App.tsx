import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AppLayout } from './layout/AppLayout';
import { Login } from './pages/auth/Login';
import { Dashboard } from './pages/entrepreneur/Dashboard';
import { ProductsCatalog } from './pages/entrepreneur/ProductsCatalog';
import { ApplicationWizard } from './pages/entrepreneur/ApplicationWizard';
import { ApplicationDetail } from './pages/entrepreneur/ApplicationDetail';
import { History } from './pages/entrepreneur/History';
import { UnderwriterQueue } from './pages/bank/UnderwriterQueue';
import { UnderwriterReview } from './pages/bank/UnderwriterReview';

const ProtectedRoute: React.FC<{ children: React.ReactNode; officerOnly?: boolean }> = ({
  children,
  officerOnly = false,
}) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-xs text-gray-400">
        Загрузка кредитного конвейера...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (officerOnly && user.role !== 'BANK_OFFICER') {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            {/* Entrepreneur Routes */}
            <Route path="/" element={<Dashboard />} />
            <Route path="/products" element={<ProductsCatalog />} />
            <Route path="/apply" element={<ApplicationWizard />} />
            <Route path="/applications/:id" element={<ApplicationDetail />} />
            <Route path="/history" element={<History />} />

            {/* Bank Officer Routes */}
            <Route
              path="/bank"
              element={
                <ProtectedRoute officerOnly>
                  <UnderwriterQueue />
                </ProtectedRoute>
              }
            />
            <Route
              path="/bank/applications/:id"
              element={
                <ProtectedRoute officerOnly>
                  <UnderwriterReview />
                </ProtectedRoute>
              }
            />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
