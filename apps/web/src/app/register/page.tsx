'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { api, ApiError } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input, Label } from '@/components/ui/input';
import { Card } from '@/components/ui/card';

export default function RegisterPage() {
  const { login } = useAuth();
  const [form, setForm] = useState({
    organizationName: '',
    countryCode: 'AL',
    fullName: '',
    email: '',
    password: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const res = await api.post<{ accessToken: string }>('/auth/register', form);
      await login(res.accessToken);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.');
    } finally {
      setSubmitting(false);
    }
  }

  function update(key: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) => setForm((f) => ({ ...f, [key]: e.target.value }));
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-8">
      <Card className="w-full max-w-sm p-6">
        <h1 className="mb-1 text-xl font-semibold">Set up your clinic</h1>
        <p className="mb-6 text-sm text-gray-500">Creates your organization and an Owner/Admin account.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="organizationName">Clinic name</Label>
            <Input id="organizationName" required value={form.organizationName} onChange={update('organizationName')} />
          </div>
          <div>
            <Label htmlFor="countryCode">Country code (ISO 2-letter)</Label>
            <Input id="countryCode" required maxLength={2} value={form.countryCode} onChange={update('countryCode')} />
          </div>
          <div>
            <Label htmlFor="fullName">Your full name</Label>
            <Input id="fullName" required value={form.fullName} onChange={update('fullName')} />
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" required value={form.email} onChange={update('email')} />
          </div>
          <div>
            <Label htmlFor="password">Password (min 12 characters)</Label>
            <Input id="password" type="password" required minLength={12} value={form.password} onChange={update('password')} />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? 'Creating...' : 'Create clinic'}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-500">
          Already have an account?{' '}
          <Link href="/login" className="text-blue-600 hover:underline">
            Log in
          </Link>
        </p>
      </Card>
    </div>
  );
}
