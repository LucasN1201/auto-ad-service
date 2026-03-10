'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const TOKEN_KEY = 'auto_ad_jwt';

type AuthContextType = {
  token: string | null;
  login: (t: string) => void;
  logout: () => void;
  isReady: boolean;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const stored = typeof window !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null;
    setToken(stored);
    setIsReady(true);
  }, []);

  const login = useCallback((t: string) => {
    setToken(t);
    if (typeof window !== 'undefined') localStorage.setItem(TOKEN_KEY, t);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    if (typeof window !== 'undefined') localStorage.removeItem(TOKEN_KEY);
  }, []);

  return (
    <AuthContext.Provider value={{ token, login, logout, isReady }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
