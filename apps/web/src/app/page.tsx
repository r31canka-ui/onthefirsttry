'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { getDefaultRoute } from '@/lib/routes';

export default function RootPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      router.replace(user ? getDefaultRoute(user) : '/login');
    }
  }, [loading, user, router]);

  return null;
}
