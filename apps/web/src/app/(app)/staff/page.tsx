'use client';

import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '@/lib/api';
import { Role, StaffMember } from '@/lib/types';
import { Card, Badge } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input, Label, Select } from '@/components/ui/input';

export default function StaffPage() {
  const queryClient = useQueryClient();
  const [showInvite, setShowInvite] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: staff, isLoading } = useQuery({
    queryKey: ['staff'],
    queryFn: () => api.get<StaffMember[]>('/staff'),
  });
  const { data: roles } = useQuery({ queryKey: ['roles'], queryFn: () => api.get<Role[]>('/roles') });

  const inviteMutation = useMutation({
    mutationFn: (payload: { email: string; fullName: string; roleIds: string[] }) =>
      api.post('/staff/invite', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff'] });
      setShowInvite(false);
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : 'Failed to invite.'),
  });

  const disableMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/staff/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['staff'] }),
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Staff</h1>
        <Button onClick={() => setShowInvite((v) => !v)}>{showInvite ? 'Cancel' : 'Invite staff'}</Button>
      </div>

      {showInvite && roles && (
        <InviteForm
          roles={roles}
          submitting={inviteMutation.isPending}
          error={error}
          onSubmit={(payload) => {
            setError(null);
            inviteMutation.mutate(payload);
          }}
        />
      )}

      <Card className="overflow-x-auto">
        {isLoading ? (
          <p className="p-4 text-sm text-gray-500">Loading...</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="border-b border-gray-200 text-left text-gray-500">
              <tr>
                <th className="px-4 py-2">Name</th>
                <th className="px-4 py-2">Email</th>
                <th className="px-4 py-2">Role(s)</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2" />
              </tr>
            </thead>
            <tbody>
              {staff?.map((s) => (
                <tr key={s.id} className="border-b border-gray-100 last:border-0">
                  <td className="px-4 py-2 font-medium">{s.fullName}</td>
                  <td className="px-4 py-2 text-gray-600">{s.email}</td>
                  <td className="px-4 py-2">
                    {s.userRoles.map(({ role }) => (
                      <Badge key={role.id} className="mr-1 bg-gray-100 text-gray-700">
                        {role.name}
                      </Badge>
                    ))}
                  </td>
                  <td className="px-4 py-2 text-gray-600">{s.status}</td>
                  <td className="px-4 py-2 text-right">
                    {s.status !== 'disabled' && (
                      <Button variant="danger" onClick={() => disableMutation.mutate(s.id)}>
                        Disable
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}

function InviteForm({
  roles,
  onSubmit,
  submitting,
  error,
}: {
  roles: Role[];
  onSubmit: (payload: { email: string; fullName: string; roleIds: string[] }) => void;
  submitting: boolean;
  error: string | null;
}) {
  const [form, setForm] = useState({ email: '', fullName: '', roleId: roles[0]?.id ?? '' });

  return (
    <Card className="p-4">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit({ email: form.email, fullName: form.fullName, roleIds: [form.roleId] });
        }}
        className="grid grid-cols-1 gap-3 sm:grid-cols-4"
      >
        <div>
          <Label>Full name</Label>
          <Input required value={form.fullName} onChange={(e) => setForm((f) => ({ ...f, fullName: e.target.value }))} />
        </div>
        <div>
          <Label>Email</Label>
          <Input
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
          />
        </div>
        <div>
          <Label>Role</Label>
          <Select value={form.roleId} onChange={(e) => setForm((f) => ({ ...f, roleId: e.target.value }))}>
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </Select>
        </div>
        <div className="flex items-end">
          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? 'Sending...' : 'Send invite'}
          </Button>
        </div>
        {error && <p className="sm:col-span-4 text-sm text-red-600">{error}</p>}
      </form>
    </Card>
  );
}
