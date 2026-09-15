'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Contact } from '@/lib/types';
import { Card, Badge } from '@/components/ui/card';
import { Input, Select } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/lib/auth-context';

const STATUS_LABELS: Record<string, string> = {
  lead: 'Lead',
  active_patient: 'Active Patient',
  inactive: 'Inactive',
};

const STATUS_COLORS: Record<string, string> = {
  lead: 'bg-amber-100 text-amber-800',
  active_patient: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-600',
};

export default function ContactsPage() {
  const { hasPermission } = useAuth();
  const [q, setQ] = useState('');
  const [status, setStatus] = useState('');
  const [showNew, setShowNew] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['contacts', q, status],
    queryFn: () =>
      api.get<{ items: Contact[]; total: number }>(
        `/contacts?${new URLSearchParams({ ...(q && { q }), ...(status && { status }) }).toString()}`,
      ),
  });

  const createMutation = useMutation({
    mutationFn: (payload: { firstName: string; lastName: string; email: string; phone: string }) =>
      api.post<Contact>('/contacts', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      setShowNew(false);
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Contacts</h1>
        {hasPermission('contacts.write') && (
          <Button onClick={() => setShowNew((v) => !v)}>{showNew ? 'Cancel' : 'New contact'}</Button>
        )}
      </div>

      {showNew && (
        <NewContactForm
          onSubmit={(payload) => createMutation.mutate(payload)}
          submitting={createMutation.isPending}
        />
      )}

      <div className="flex flex-wrap gap-3">
        <Input
          placeholder="Search name, email, phone..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        <Select value={status} onChange={(e) => setStatus(e.target.value)} className="max-w-[180px]">
          <option value="">All statuses</option>
          <option value="lead">Lead</option>
          <option value="active_patient">Active Patient</option>
          <option value="inactive">Inactive</option>
        </Select>
      </div>

      <Card className="overflow-x-auto">
        {isLoading ? (
          <p className="p-4 text-sm text-gray-500">Loading...</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="border-b border-gray-200 text-left text-gray-500">
              <tr>
                <th className="px-4 py-2">Name</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Stage</th>
                <th className="px-4 py-2">Email</th>
                <th className="px-4 py-2">Phone</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((c) => (
                <tr key={c.id} className="border-b border-gray-100 last:border-0 hover:bg-gray-50">
                  <td className="px-4 py-2">
                    <Link href={`/contacts/${c.id}`} className="font-medium text-blue-600 hover:underline">
                      {c.firstName} {c.lastName}
                    </Link>
                  </td>
                  <td className="px-4 py-2">
                    <Badge className={STATUS_COLORS[c.status]}>{STATUS_LABELS[c.status]}</Badge>
                  </td>
                  <td className="px-4 py-2 text-gray-600">{c.pipelineStage?.name ?? '-'}</td>
                  <td className="px-4 py-2 text-gray-600">{c.email ?? '-'}</td>
                  <td className="px-4 py-2 text-gray-600">{c.phone ?? '-'}</td>
                </tr>
              ))}
              {data?.items.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-6 text-center text-gray-500">
                    No contacts found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}

function NewContactForm({
  onSubmit,
  submitting,
}: {
  onSubmit: (payload: { firstName: string; lastName: string; email: string; phone: string }) => void;
  submitting: boolean;
}) {
  const [form, setForm] = useState({ firstName: '', lastName: '', email: '', phone: '' });
  return (
    <Card className="p-4">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit(form);
        }}
        className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4"
      >
        <Input
          placeholder="First name"
          required
          value={form.firstName}
          onChange={(e) => setForm((f) => ({ ...f, firstName: e.target.value }))}
        />
        <Input
          placeholder="Last name"
          value={form.lastName}
          onChange={(e) => setForm((f) => ({ ...f, lastName: e.target.value }))}
        />
        <Input
          placeholder="Email"
          type="email"
          value={form.email}
          onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
        />
        <Input
          placeholder="Phone"
          value={form.phone}
          onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
        />
        <Button type="submit" disabled={submitting} className="sm:col-span-2 lg:col-span-1">
          {submitting ? 'Saving...' : 'Save contact'}
        </Button>
      </form>
    </Card>
  );
}
