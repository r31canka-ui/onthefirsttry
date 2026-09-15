export interface CurrentUser {
  userId: string;
  organizationId: string;
  fullName: string;
  email: string;
  permissions: string[];
}

export interface PipelineStage {
  id: string;
  name: string;
  position: number;
  isWonStage: boolean;
}

export interface Tag {
  id: string;
  name: string;
  color?: string | null;
}

export interface Contact {
  id: string;
  firstName: string;
  lastName?: string | null;
  email?: string | null;
  phone?: string | null;
  status: 'lead' | 'active_patient' | 'inactive';
  source?: string | null;
  pipelineStageId?: string | null;
  pipelineStage?: PipelineStage | null;
  assignedToUserId?: string | null;
  tags: { tag: Tag }[];
  createdAt: string;
  updatedAt: string;
}

export interface ContactActivity {
  id: string;
  type: string;
  body?: string | null;
  isClinical: boolean;
  createdAt: string;
  author?: { id: string; fullName: string } | null;
}

export interface Location {
  id: string;
  name: string;
  address?: string | null;
  city?: string | null;
  timezone: string;
  isActive: boolean;
}

export interface Service {
  id: string;
  name: string;
  category?: string | null;
  durationMinutes: number;
  priceCents: number;
  currency: string;
  isActive: boolean;
}

export interface Appointment {
  id: string;
  status: 'scheduled' | 'completed' | 'cancelled' | 'no_show';
  startsAt: string;
  endsAt: string;
  contact: Contact;
  provider: { id: string; fullName: string };
  service: Service;
  location: Location;
}

export interface StaffMember {
  id: string;
  fullName: string;
  email: string;
  status: string;
  userRoles: { role: { id: string; name: string } }[];
}

export interface Role {
  id: string;
  name: string;
  isSystemDefault: boolean;
  rolePermissions: { permission: { key: string; description: string } }[];
}

export interface DashboardSummary {
  leadsThisWeek: number;
  pipelineByStage: { name: string; count: number }[];
  conversionRate: number;
  appointmentsThisWeek: Record<string, number>;
  upcomingAppointments: Appointment[];
}
