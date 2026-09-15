'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Contact, ContactActivity, PipelineStage } from '@/lib/types';
import { Card, Badge } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/input';
import { useAuth } from '@/lib/auth-context';

export default function ContactDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const { hasPermission } = useAuth();
  const queryClient = useQueryClient();
  const [note, setNote] = useState('');
  const [isClinical, setIsClinical] = useState(false);

  const { data: contact } = useQuery({
    queryKey: ['contact', id],
    queryFn: () => api.get<Contact>(`/contacts/${id}`),
  });

  const { data: activity } = useQuery({
    queryKey: ['contact-activity', id],
    queryFn: () => api.get<ContactActivity[]>(`/contacts/${id}/activity`),
  });

  const { data: stages } = useQuery({
    queryKey: ['pipeline-stages'],
    queryFn: () => api.get<PipelineStage[]>('/pipeline-stages'),
  });

  const moveStage = useMutation({
    mutationFn: (pipelineStageId: string) => api.post(`/contacts/${id}/stage`, { pipelineStageId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contact', id] });
      queryClient.invalidateQueries({ queryKey: ['contact-activity', id] });
    },
  });

  const addActivity = useMutation({
    mutationFn: () => api.post(`/contacts/${id}/activity`, { body: note, isClinical }),
    onSuccess: () => {
      setNote('');
      setIsClinical(false);
      queryClient.invalidateQueries({ queryKey: ['contact-activity', id] });
    },
  });

  if (!contact) return <p className="text-sm text-gray-500">Loading...</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">
          {contact.firstName} {contact.lastName}
        </h1>
        <div className="mt-1 flex flex-wrap gap-2 text-sm text-gray-500">
          {contact.email && <span>{contact.email}</span>}
          {contact.phone && <span>&middot; {contact.phone}</span>}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="p-4 lg:col-span-1">
          <h2 className="mb-3 font-medium">Pipeline stage</h2>
          {hasPermission('contacts.write') ? (
            <Select
              value={contact.pipelineStageId ?? ''}
              onChange={(e) => moveStage.mutate(e.target.value)}
            >
              <option value="" disabled>
                Select a stage
              </option>
              {stages?.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </Select>
          ) : (
            <p className="text-sm text-gray-700">{contact.pipelineStage?.name ?? '-'}</p>
          )}

          <h2 className="mt-6 mb-2 font-medium">Tags</h2>
          <div className="flex flex-wrap gap-1">
            {contact.tags.map(({ tag }) => (
              <Badge key={tag.id} className="bg-gray-100 text-gray-700">
                {tag.name}
              </Badge>
            ))}
            {contact.tags.length === 0 && <p className="text-sm text-gray-500">No tags.</p>}
          </div>
        </Card>

        <Card className="p-4 lg:col-span-2">
          <h2 className="mb-3 font-medium">Activity</h2>

          {hasPermission('contacts.write') && (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (note.trim()) addActivity.mutate();
              }}
              className="mb-4 space-y-2"
            >
              <textarea
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                rows={3}
                placeholder="Add a note..."
                value={note}
                onChange={(e) => setNote(e.target.value)}
              />
              <div className="flex items-center justify-between">
                {hasPermission('clinical_notes.write') && (
                  <label className="flex items-center gap-2 text-sm text-gray-600">
                    <input
                      type="checkbox"
                      checked={isClinical}
                      onChange={(e) => setIsClinical(e.target.checked)}
                    />
                    Clinical note
                  </label>
                )}
                <Button type="submit" disabled={addActivity.isPending || !note.trim()}>
                  {addActivity.isPending ? 'Saving...' : 'Add note'}
                </Button>
              </div>
            </form>
          )}

          <ul className="space-y-3">
            {activity?.map((a) => (
              <li key={a.id} className="border-t border-gray-100 pt-3 first:border-0 first:pt-0">
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span>{new Date(a.createdAt).toLocaleString()}</span>
                  {a.author && <span>&middot; {a.author.fullName}</span>}
                  {a.isClinical && <Badge className="bg-purple-100 text-purple-700">Clinical</Badge>}
                  {a.type === 'stage_change' && <Badge className="bg-blue-100 text-blue-700">Stage change</Badge>}
                </div>
                <p className="mt-1 text-sm text-gray-800">{a.body}</p>
              </li>
            ))}
            {activity?.length === 0 && <p className="text-sm text-gray-500">No activity yet.</p>}
          </ul>
        </Card>
      </div>
    </div>
  );
}
