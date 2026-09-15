'use client';

import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { api } from './api';
import { CurrentUser } from './types';

interface AuthContextValue {
  user: CurrentUser | null;
  loading: boolean;
  login: (accessToken: string) => Promise<void>;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchMe = useCallback(async () => {
    try {
      const me = await api.get<CurrentUser>('/auth/me');
      setUser(me);
    } catch {
      setUser(null);
      try {
        localStorage.removeItem('accessToken');
      } catch {
        // ignore
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const hasToken = typeof window !== 'undefined' && localStorage.getItem('accessToken');
    if (hasToken) {
      fetchMe();
    } else {
      setLoading(false);
    }
  }, [fetchMe]);

  const login = useCallback(
    async (accessToken: string) => {
      localStorage.setItem('accessToken', accessToken);
      await fetchMe();
      router.push('/dashboard');
    },
    [fetchMe, router],
  );

  const logout = useCallback(() => {
    localStorage.removeItem('accessToken');
    setUser(null);
    router.push('/login');
  }, [router]);

  const hasPermission = useCallback(
    (permission: string) => user?.permissions.includes(permission) ?? false,
    [user],
  );

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
