'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { api, ApiError } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input, Label } from '@/components/ui/input';
import { Card } from '@/components/ui/card';

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [tempToken, setTempToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const res = await api.post<{ accessToken?: string; requiresTwoFactor?: boolean; tempToken?: string }>(
        '/auth/login',
        { email, password },
      );
      if (res.requiresTwoFactor && res.tempToken) {
        setTempToken(res.tempToken);
      } else if (res.accessToken) {
        await login(res.accessToken);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleVerify2fa(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const res = await api.post<{ accessToken: string }>('/auth/login/2fa', { tempToken, code });
      await login(res.accessToken);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <Card className="w-full max-w-sm p-6">
        <h1 className="mb-6 text-xl font-semibold">Log in to Clinic CRM</h1>

        {!tempToken ? (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <Button type="submit" disabled={submitting} className="w-full">
              {submitting ? 'Logging in...' : 'Log in'}
            </Button>
          </form>
        ) : (
          <form onSubmit={handleVerify2fa} className="space-y-4">
            <p className="text-sm text-gray-600">Enter the 6-digit code from your authenticator app.</p>
            <Input value={code} onChange={(e) => setCode(e.target.value)} maxLength={6} required autoFocus />
            {error && <p className="text-sm text-red-600">{error}</p>}
            <Button type="submit" disabled={submitting} className="w-full">
              Verify
            </Button>
          </form>
        )}

        <p className="mt-6 text-center text-sm text-gray-500">
          No account?{' '}
          <Link href="/register" className="text-blue-600 hover:underline">
            Register your clinic
          </Link>
        </p>
      </Card>
    </div>
  );
}
