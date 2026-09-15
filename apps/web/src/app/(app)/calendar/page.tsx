'use client';

import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '@/lib/api';
import { Appointment, Contact, Location, Service } from '@/lib/types';
import { Card, Badge } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input, Select, Label } from '@/components/ui/input';
import { useAuth } from '@/lib/auth-context';

const STATUS_COLORS: Record<string, string> = {
  scheduled: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  cancelled: 'bg-gray-100 text-gray-500',
  no_show: 'bg-red-100 text-red-700',
};

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export default function CalendarPage() {
  const { hasPermission } = useAuth();
  const queryClient = useQueryClient();
  const [date, setDate] = useState(todayIso());
  const [showBooking, setShowBooking] = useState(false);

  const dayStart = `${date}T00:00:00.000Z`;
  const dayEnd = `${date}T23:59:59.999Z`;

  const { data: appointments, isLoading } = useQuery({
    queryKey: ['appointments', date],
    queryFn: () => api.get<Appointment[]>(`/appointments?from=${dayStart}&to=${dayEnd}`),
  });

  const cancelMutation = useMutation({
    mutationFn: (id: string) => api.post(`/appointments/${id}/cancel`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['appointments', date] }),
  });
  const completeMutation = useMutation({
    mutationFn: (id: string) => api.post(`/appointments/${id}/complete`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['appointments', date] }),
  });
  const noShowMutation = useMutation({
    mutationFn: (id: string) => api.post(`/appointments/${id}/no-show`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['appointments', date] }),
  });

  const sorted = useMemo(
    () => [...(appointments ?? [])].sort((a, b) => a.startsAt.localeCompare(b.startsAt)),
    [appointments],
  );

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Calendar</h1>
        {hasPermission('appointments.write') && (
          <Button onClick={() => setShowBooking((v) => !v)}>{showBooking ? 'Cancel' : 'Book appointment'}</Button>
        )}
      </div>

      <Input type="date" value={date} onChange={(e) => setDate(e.target.value)} className="max-w-[200px]" />

      {showBooking && (
        <BookingForm
          date={date}
          onBooked={() => {
            setShowBooking(false);
            queryClient.invalidateQueries({ queryKey: ['appointments', date] });
          }}
        />
      )}

      <Card className="divide-y divide-gray-100">
        {isLoading && <p className="p-4 text-sm text-gray-500">Loading...</p>}
        {!isLoading && sorted.length === 0 && (
          <p className="p-4 text-sm text-gray-500">No appointments for this day.</p>
        )}
        {sorted.map((appt) => (
          <div key={appt.id} className="flex flex-wrap items-center justify-between gap-3 p-4">
            <div>
              <div className="text-sm font-medium text-gray-900">
                {new Date(appt.startsAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} -{' '}
                {new Date(appt.endsAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
              <div className="text-sm text-gray-700">
                {appt.contact.firstName} {appt.contact.lastName} &middot; {appt.service.name} with{' '}
                {appt.provider.fullName} @ {appt.location.name}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge className={STATUS_COLORS[appt.status]}>{appt.status.replace('_', ' ')}</Badge>
              {appt.status === 'scheduled' && hasPermission('appointments.write') && (
                <>
                  <Button variant="secondary" onClick={() => completeMutation.mutate(appt.id)}>
                    Complete
                  </Button>
                  <Button variant="secondary" onClick={() => noShowMutation.mutate(appt.id)}>
                    No-show
                  </Button>
                  <Button variant="danger" onClick={() => cancelMutation.mutate(appt.id)}>
                    Cancel
                  </Button>
                </>
              )}
            </div>
          </div>
        ))}
      </Card>
    </div>
  );
}

function BookingForm({ date, onBooked }: { date: string; onBooked: () => void }) {
  const { data: locations } = useQuery({ queryKey: ['locations'], queryFn: () => api.get<Location[]>('/locations') });
  const { data: services } = useQuery({ queryKey: ['services'], queryFn: () => api.get<Service[]>('/services') });
  const { data: staff } = useQuery({
    queryKey: ['staff-for-booking'],
    queryFn: () => api.get<{ id: string; fullName: string }[]>('/staff'),
  });
  const [contactQuery, setContactQuery] = useState('');
  const { data: contactResults } = useQuery({
    queryKey: ['contact-search', contactQuery],
    queryFn: () => api.get<{ items: Contact[] }>(`/contacts?q=${encodeURIComponent(contactQuery)}`),
    enabled: contactQuery.length >= 2,
  });

  const [form, setForm] = useState({ contactId: '', providerUserId: '', serviceId: '', locationId: '', startsAt: '' });
  const [error, setError] = useState<string | null>(null);

  const { data: slots } = useQuery({
    queryKey: ['availability', form.providerUserId, form.serviceId, form.locationId, date],
    queryFn: () =>
      api.get<{ startsAt: string }[]>(
        `/appointments/availability?providerId=${form.providerUserId}&serviceId=${form.serviceId}&locationId=${form.locationId}&date=${date}`,
      ),
    enabled: Boolean(form.providerUserId && form.serviceId && form.locationId),
  });

  const bookMutation = useMutation({
    mutationFn: () => api.post('/appointments', form),
    onSuccess: onBooked,
    onError: (err) => setError(err instanceof ApiError ? err.message : 'Failed to book.'),
  });

  return (
    <Card className="p-4">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          setError(null);
          bookMutation.mutate();
        }}
        className="space-y-3"
      >
        <div>
          <Label>Patient / lead</Label>
          <Input
            placeholder="Search by name, email, phone..."
            value={contactQuery}
            onChange={(e) => setContactQuery(e.target.value)}
          />
          {contactResults && contactResults.items.length > 0 && (
            <div className="mt-1 max-h-32 overflow-y-auto rounded-md border border-gray-200">
              {contactResults.items.map((c) => (
                <button
                  type="button"
                  key={c.id}
                  onClick={() => {
                    setForm((f) => ({ ...f, contactId: c.id }));
                    setContactQuery(`${c.firstName} ${c.lastName ?? ''}`);
                  }}
                  className="block w-full px-3 py-1.5 text-left text-sm hover:bg-gray-50"
                >
                  {c.firstName} {c.lastName}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div>
            <Label>Location</Label>
            <Select
              value={form.locationId}
              onChange={(e) => setForm((f) => ({ ...f, locationId: e.target.value }))}
              required
            >
              <option value="">Select</option>
              {locations?.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.name}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <Label>Service</Label>
            <Select
              value={form.serviceId}
              onChange={(e) => setForm((f) => ({ ...f, serviceId: e.target.value }))}
              required
            >
              <option value="">Select</option>
              {services?.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.durationMinutes}min)
                </option>
              ))}
            </Select>
          </div>
          <div>
            <Label>Provider</Label>
            <Select
              value={form.providerUserId}
              onChange={(e) => setForm((f) => ({ ...f, providerUserId: e.target.value }))}
              required
            >
              <option value="">Select</option>
              {staff?.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.fullName}
                </option>
              ))}
            </Select>
          </div>
        </div>

        {slots && (
          <div>
            <Label>Available slots on {date}</Label>
            <div className="flex flex-wrap gap-2">
              {slots.slice(0, 24).map((slot) => (
                <button
                  type="button"
                  key={slot.startsAt}
                  onClick={() => setForm((f) => ({ ...f, startsAt: slot.startsAt }))}
                  className={`rounded-md border px-2 py-1 text-xs ${
                    form.startsAt === slot.startsAt
                      ? 'border-blue-600 bg-blue-50 text-blue-700'
                      : 'border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {new Date(slot.startsAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </button>
              ))}
              {slots.length === 0 && <p className="text-sm text-gray-500">No open slots that day.</p>}
            </div>
          </div>
        )}

        {error && <p className="text-sm text-red-600">{error}</p>}

        <Button type="submit" disabled={!form.contactId || !form.startsAt || bookMutation.isPending}>
          {bookMutation.isPending ? 'Booking...' : 'Confirm booking'}
        </Button>
      </form>
    </Card>
  );
}
