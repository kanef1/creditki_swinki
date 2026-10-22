import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { authApi, demoApi } from '../api/client';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  quickLogin: (username: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('alfa_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('alfa_token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (token) {
      authApi
        .getMe()
        .then((fetchedUser) => {
          setUser(fetchedUser);
          localStorage.setItem('alfa_user', JSON.stringify(fetchedUser));
        })
        .catch(() => {
          setUser(null);
          setToken(null);
          localStorage.removeItem('alfa_token');
          localStorage.removeItem('alfa_user');
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const login = async (username: string, password: string) => {
    const res = await authApi.login(username, password);
    setToken(res.token);
    setUser(res.user);
    localStorage.setItem('alfa_token', res.token);
    localStorage.setItem('alfa_user', JSON.stringify(res.user));
  };

  const quickLogin = async (username: string) => {
    const res = await demoApi.quickLogin(username);
    setToken(res.token);
    setUser(res.user);
    localStorage.setItem('alfa_token', res.token);
    localStorage.setItem('alfa_user', JSON.stringify(res.user));
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
    setToken(null);
  };

  const refreshUser = async () => {
    if (token) {
      const fetched = await authApi.getMe();
      setUser(fetched);
      localStorage.setItem('alfa_user', JSON.stringify(fetched));
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, quickLogin, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
