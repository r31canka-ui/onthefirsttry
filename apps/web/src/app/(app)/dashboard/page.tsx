'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { api } from '@/lib/api';
import { DashboardSummary } from '@/lib/types';
import { Card } from '@/components/ui/card';

export default function DashboardPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () => api.get<DashboardSummary>('/dashboard/summary'),
  });

  if (isLoading) return <p className="text-sm text-gray-500">Loading dashboard...</p>;
  if (error) return <p className="text-sm text-red-600">Failed to load dashboard.</p>;
  if (!data) return null;

  const appts = data.appointmentsThisWeek;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Leads this week" value={data.leadsThisWeek} />
        <StatCard label="Conversion rate" value={`${data.conversionRate}%`} />
        <StatCard label="Booked this week" value={appts.scheduled + appts.completed + appts.no_show} />
        <StatCard label="No-shows this week" value={appts.no_show} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="p-4">
          <h2 className="mb-3 font-medium">Pipeline</h2>
          <ul className="space-y-2">
            {data.pipelineByStage.map((stage) => (
              <li key={stage.name} className="flex items-center justify-between text-sm">
                <span className="text-gray-700">{stage.name}</span>
                <span className="font-medium">{stage.count}</span>
              </li>
            ))}
          </ul>
        </Card>

        <Card className="p-4">
          <h2 className="mb-3 font-medium">Upcoming appointments</h2>
          {data.upcomingAppointments.length === 0 && (
            <p className="text-sm text-gray-500">Nothing scheduled.</p>
          )}
          <ul className="space-y-3">
            {data.upcomingAppointments.map((appt) => (
              <li key={appt.id} className="text-sm">
                <Link href={`/contacts/${appt.contact.id}`} className="font-medium text-blue-600 hover:underline">
                  {appt.contact.firstName} {appt.contact.lastName}
                </Link>
                <div className="text-gray-500">
                  {new Date(appt.startsAt).toLocaleString()} - {appt.service.name} with {appt.provider.fullName}
                </div>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card className="p-4">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="mt-1 text-2xl font-semibold">{value}</div>
    </Card>
  );
}
